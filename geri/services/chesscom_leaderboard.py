import chessdotcom as cdc

from geri.repository.users import list_chesscom_usernames
from geri.services.chesscom_bootstrap import ensure_chesscom_configured
from geri.utils.discord_safe import clip_message


def format_cdc_leaderboard(perf: str = "blitz") -> str:
    ensure_chesscom_configured()
    players = list_chesscom_usernames()
    if not players:
        return (
            f"**Chess.com {perf.title()} Ratings**\n"
            "No Chess.com usernames in the database yet. Use `/addcdc` or `$addcdc`."
        )
    leaderboardtxt = f"**Chess.com {perf.title()} Ratings** \n"
    playerlist: list[list] = []
    word = "last"
    word2 = "rating"
    perf_key = f"chess_{perf}"

    if perf_key == "chess_streak":
        word = "best"
        word2 = "score"
        perf_key = "puzzle_rush"

    for player in players:
        try:
            ratings = cdc.get_player_stats(player)
            val = ratings.json["stats"][perf_key][word][word2]
            if val:
                playerlist.append([player, val])
        except Exception:
            continue

    leaderboard = sorted(playerlist, key=lambda item: item[1], reverse=True)

    for row in leaderboard:
        leaderboardtxt += f"{row[0]}: {row[1]}\n"

    return clip_message(leaderboardtxt)
