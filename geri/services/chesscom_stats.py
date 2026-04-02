import chessdotcom as cdc

from geri.services.chesscom_bootstrap import ensure_chesscom_configured

# (embed key, chess.com stats API key)
_RATING_MODES: tuple[tuple[str, str], ...] = (
    ("bullet", "chess_bullet"),
    ("blitz", "chess_blitz"),
    ("rapid", "chess_rapid"),
    ("classical", "chess_classical"),
    ("correspondence", "chess_correspondence"),
)


def _last_rating(stats_root: dict, api_key: str) -> int | None:
    try:
        v = stats_root[api_key]["last"]["rating"]
        return int(v) if v is not None else None
    except Exception:
        return None


def _extract_ratings(stats_root: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, api_key in _RATING_MODES:
        r = _last_rating(stats_root, api_key)
        if r is not None:
            out[key] = r
    if "correspondence" not in out:
        r = _last_rating(stats_root, "chess_daily")
        if r is not None:
            out["correspondence"] = r
    return out


def _country_code_from_url(url: str | None) -> str | None:
    if not url or not isinstance(url, str):
        return None
    parts = url.rstrip("/").split("/")
    return parts[-1].upper() if parts else None


def chessdotcom_stats(username: str) -> dict:
    """
    Player ratings for profile UI.
    Keys: chesscom_username, online (bool | None), ratings, tactics_highest,
    chess960_rating, puzzle_rush_best.
    """
    ensure_chesscom_configured()
    p1 = username.strip().lower()
    ratings = cdc.get_player_stats(p1)
    stats_root = ratings.json.get("stats") or {}

    out: dict = {
        "chesscom_username": p1,
        "online": None,
        "ratings": _extract_ratings(stats_root),
        "tactics_highest": None,
        "chess960_rating": None,
        "puzzle_rush_best": None,
    }
    try:
        out["online"] = bool(cdc.is_player_online(p1).json.get("online"))
    except Exception:
        pass

    try:
        th = stats_root["tactics"]["highest"]["rating"]
        if th is not None:
            out["tactics_highest"] = int(th)
    except Exception:
        pass

    try:
        r960 = stats_root["chess960_daily"]["last"]["rating"]
        if r960 is not None:
            out["chess960_rating"] = int(r960)
    except Exception:
        pass

    try:
        pr = stats_root["puzzle_rush"]["best"]
        if pr.get("score") is not None:
            out["puzzle_rush_best"] = int(pr["score"])
    except Exception:
        pass

    return out


def fetch_profile_display(username: str) -> dict:
    """Public profile fields from Chess.com (best-effort)."""
    ensure_chesscom_configured()
    p1 = username.strip().lower()
    fallback_url = f"https://www.chess.com/member/{p1}"
    empty = {
        "chesscom_username": p1,
        "avatar_url": None,
        "profile_url": fallback_url,
        "title": None,
        "display_name": None,
        "location": None,
        "country_code": None,
        "followers": None,
        "joined_ts": None,
        "is_streamer": False,
        "stream_urls": [],
        "verified": False,
    }
    try:
        r = cdc.get_player_profile(p1)
        player = r.json.get("player") or {}
        country_url = player.get("country")
        stream_urls: list[str] = []
        if tu := player.get("twitch_url"):
            stream_urls.append(tu)
        for sp in player.get("streaming_platforms") or []:
            u = sp.get("channel_url")
            if isinstance(u, str) and u and u not in stream_urls:
                stream_urls.append(u)

        joined = player.get("joined")
        followers = player.get("followers")

        return {
            "chesscom_username": player.get("username") or p1,
            "avatar_url": player.get("avatar"),
            "profile_url": player.get("url") or fallback_url,
            "title": (player.get("title") or "").strip() or None,
            "display_name": (player.get("name") or "").strip() or None,
            "location": (player.get("location") or "").strip() or None,
            "country_code": _country_code_from_url(country_url),
            "followers": int(followers) if followers is not None else None,
            "joined_ts": int(joined) if joined is not None else None,
            "is_streamer": bool(player.get("is_streamer")),
            "stream_urls": stream_urls,
            "verified": bool(player.get("verified")),
        }
    except Exception:
        return empty
