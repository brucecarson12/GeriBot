import io
import os
import re

import chess.pgn
import pgn2gif
import chessdotcom as cdc
from chessdotcom.errors import ChessDotComClientError

from geri.services.chesscom_bootstrap import ensure_chesscom_configured
from geri.utils.paths import ensure_temp_dir

# Year/month anywhere in archive URL (trailing slash / query tolerated)
_ARCHIVE_MONTH_RE = re.compile(r"/games/(\d{4})/(\d{2})", re.IGNORECASE)


def fetch_last_game_dict(username: str) -> dict:
    """
    Most recent finished game: official archives list (newest month first),
    then last game in that month (chronological order within the month).
    """
    ensure_chesscom_configured()
    raw_name = username.strip()
    p1 = raw_name.lower()
    if not p1:
        raise ValueError("Chess.com username is empty.")

    try:
        archives_resp = cdc.get_player_game_archives(p1)
    except ChessDotComClientError as e:
        if e.status_code == 404:
            raise ValueError(
                f"No Chess.com profile/archives for **{raw_name}**. "
                "Use the exact username from the profile URL (usually all lowercase)."
            ) from e
        raise

    urls = list(archives_resp.archives or [])
    if not urls:
        raise ValueError(
            "No finished games in Chess.com archives yet (very new account or no completed games)."
        )

    last_row = None
    for archive_url in reversed(urls):
        m = _ARCHIVE_MONTH_RE.search(archive_url)
        if not m:
            continue
        year, month = int(m.group(1)), int(m.group(2))
        try:
            month_resp = cdc.get_player_games_by_month(p1, year=year, month=month)
        except ChessDotComClientError as e:
            if e.status_code == 404:
                continue
            raise

        games = list(month_resp.games or [])
        if games:
            g = games[-1]
            last_row = {
                "pgn": g.pgn,
                "url": g.url,
                "white": {
                    "username": g.white.username if g.white else "",
                    "rating": g.white.rating if g.white else None,
                },
                "black": {
                    "username": g.black.username if g.black else "",
                    "rating": g.black.rating if g.black else None,
                },
            }
            break
        games_raw = month_resp.json.get("games") if isinstance(month_resp.json, dict) else None
        if isinstance(games_raw, list) and games_raw:
            last_row = games_raw[-1]
            break
        continue

    if last_row is None:
        raise ValueError("No recent games found in Chess.com archives for this player.")

    lastgame = last_row
    lastgamedict = {
        "pgn": lastgame["pgn"],
        "url": lastgame["url"],
        "wplayer": {
            "name": lastgame["white"]["username"],
            "rating": lastgame["white"]["rating"],
        },
        "bplayer": {
            "name": lastgame["black"]["username"],
            "rating": lastgame["black"]["rating"],
        },
        "vstxt": (
            f"{lastgame['white']['username']} _{lastgame['white']['rating']}_ vs. "
            f"{lastgame['black']['username']} _{lastgame['black']['rating']}_"
        ),
        "result": "",
    }

    lastgamedict["pgn4gif"] = re.sub(
        r"{\[%clk \d+:\d+:\d+(\.\d+)?\]} ", "", lastgame["pgn"]
    )
    lastgamedict["pgn4gif"] = re.sub(
        r" [0-9]\.\.\.|[1-9][0-9]\.\.\. ", "", lastgamedict["pgn4gif"]
    )

    temp_dir = ensure_temp_dir()
    pgn_io = io.StringIO(lastgamedict["pgn4gif"])
    gamepy = chess.pgn.read_game(pgn_io)
    if gamepy is None:
        raise ValueError("Could not read game PGN from Chess.com response.")
    temp_pgn = os.path.join(temp_dir, "temp.pgn")
    out_gif = os.path.join(temp_dir, "chess.gif")
    with open(temp_pgn, "w", encoding="utf-8") as f:
        print(gamepy, file=f)

    lastgamedict["result"] = gamepy.headers["Result"]
    reverse = 0
    if lastgamedict["bplayer"]["name"].lower() == p1:
        reverse = 1
    creator = pgn2gif.PgnToGifCreator(
        reverse=reverse, duration=0.5, ws_color="#ebecd0", bs_color="#779556"
    )
    creator.create_gif(temp_pgn, out_path=out_gif)

    return lastgamedict
