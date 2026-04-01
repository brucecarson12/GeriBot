import chessdotcom as cdc

from geri.services.chesscom_bootstrap import ensure_chesscom_configured


def chessdotcom_stats(username: str) -> dict:
    ensure_chesscom_configured()
    p1 = username.strip()
    ratings = cdc.get_player_stats(p1)
    stats: dict = {}
    modes = ["bullet", "blitz", "rapid", "classical", "correspondence"]
    emojis = [":gun:", ":cloud_lightning:", ":alarm_clock:", ":clock:", ":sunny:"]
    try:
        if cdc.is_player_online(p1).json["online"]:
            stats["txt"] = ":green_circle: Online Now!\n\n"
        else:
            stats["txt"] = ":red_circle: Offline\n\n"
    except Exception:
        stats["txt"] = "\n"
    for i in modes:
        try:
            indx = modes.index(i)
            search = "chess_" + i
            stats[i] = ratings.json["stats"][search]["last"]["rating"]
            stats["txt"] += f"{emojis[indx]} {stats[i]}  "
        except Exception:
            continue

    try:
        rush_best = ratings.json["stats"]["puzzle_rush"]["best"]["score"]
        stats["txt"] += f":jigsaw::cloud_tornado: {rush_best}"
    except Exception:
        pass
    return stats
