import asyncio

import chessdotcom as cdc

from geri.repository.users import list_chesscom_usernames
from geri.services.chesscom_bootstrap import ensure_chesscom_configured

_DEFAULT_CONCURRENCY = 12


def _fetch_player_perf_value(player: str, perf: str) -> tuple[str, int] | None:
    """Return (username, value) or None if missing/error."""
    word = "last"
    word2 = "rating"
    perf_key = f"chess_{perf}"
    if perf_key == "chess_streak":
        word = "best"
        word2 = "score"
        perf_key = "puzzle_rush"
    try:
        ratings = cdc.get_player_stats(player)
        val = ratings.json["stats"][perf_key][word][word2]
        if val is None:
            return None
        return (player, int(val))
    except Exception:
        return None


async def fetch_leaderboard_rows(
    perf: str,
    *,
    max_concurrent: int = _DEFAULT_CONCURRENCY,
) -> list[tuple[str, int]]:
    """
    Load stats for all registered Chess.com usernames concurrently (sync API in threads).
    """
    ensure_chesscom_configured()
    players = list_chesscom_usernames()
    if not players:
        return []

    sem = asyncio.Semaphore(max_concurrent)

    async def one(player: str) -> tuple[str, int] | None:
        async with sem:
            return await asyncio.to_thread(_fetch_player_perf_value, player, perf)

    results = await asyncio.gather(*(one(p) for p in players))
    rows = [r for r in results if r is not None]
    rows.sort(key=lambda item: item[1], reverse=True)
    return rows
