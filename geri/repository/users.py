"""User rows: Discord identity, Chess.com, optional dormant Lichess column."""

from typing import Any

from psycopg2.extras import RealDictCursor

from geri.db.connection import get_connection


def _row_to_record(row: dict | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "discord_user_id": row["discord_user_id"],
        "discord_name": row["discord_name"],
        "irl_name": (row["irl_name"] or "") or "",
        "chesscom_username": (row["chesscom_username"] or "") or "",
        "lichess_username": (row["lichess_username"] or "") or "",
    }


def to_legacy(record: dict[str, Any] | None) -> dict[str, Any] | None:
    """Shape compatible with older call sites (cdc, IRLname, lichess, discName, discID)."""
    if record is None:
        return None
    return {
        "discName": record["discord_name"],
        "discID": record["discord_user_id"],
        "cdc": record["chesscom_username"],
        "lichess": record["lichess_username"],
        "IRLname": record["irl_name"],
    }


def get_by_discord_id(discord_user_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM geri_users WHERE discord_user_id = %s",
                (discord_user_id,),
            )
            row = cur.fetchone()
    return _row_to_record(row)


def get_by_discord_name(discord_name: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM geri_users WHERE discord_name = %s LIMIT 1",
                (discord_name,),
            )
            row = cur.fetchone()
    return _row_to_record(row)


def upsert_chesscom(
    discord_user_id: int,
    discord_name: str,
    chesscom_username: str,
    irl_name: str | None = None,
) -> dict[str, Any]:
    # Chess.com pub API paths use lowercase usernames.
    cc = chesscom_username.strip().lower()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO geri_users (discord_user_id, discord_name, irl_name, chesscom_username)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (discord_user_id) DO UPDATE SET
                    discord_name = EXCLUDED.discord_name,
                    irl_name = COALESCE(EXCLUDED.irl_name, geri_users.irl_name),
                    chesscom_username = EXCLUDED.chesscom_username
                RETURNING *
                """,
                (
                    discord_user_id,
                    discord_name,
                    irl_name,
                    cc,
                ),
            )
            row = cur.fetchone()
    return _row_to_record(row)


def list_chesscom_usernames() -> list[str]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT chesscom_username FROM geri_users
                WHERE chesscom_username IS NOT NULL
                  AND TRIM(chesscom_username) <> ''
                ORDER BY chesscom_username
                """
            )
            rows = cur.fetchall()
    return [r["chesscom_username"].strip() for r in rows]
