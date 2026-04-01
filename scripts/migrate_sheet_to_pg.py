"""
One-time migration: Google Sheet "Chess_Tourney" -> Postgres `geri_users` table.

Requires:
  pip install gspread google-auth
  google-credentials.json in cwd (service account with sheet access)
  DATABASE_URL in environment

Sheet layout (row 1 headers, data from row 2):
  Col A: IRL name
  Col B: Lichess username  -> lichess_username (preserved, unused by bot v1)
  Col C: Discord display name
  Col D-G: tournament stats (ignored)
  Col H: Discord user ID
  Col I: Chess.com username
"""

from __future__ import annotations

import os
import sys

import gspread
import psycopg2
from psycopg2.extras import execute_values

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geri.config import normalize_database_url  # noqa: E402


def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)
    db_url = normalize_database_url(db_url)

    gc = gspread.service_account(filename="google-credentials.json")
    sheet = gc.open("Chess_Tourney").get_worksheet(0)
    rows = sheet.get_all_values()
    if len(rows) < 2:
        print("No data rows in sheet.")
        return

    data_rows = rows[1:]
    by_id: dict[int, tuple] = {}
    for row in data_rows:
        while len(row) < 9:
            row.append("")
        irl, lichess, disc_name, _, _, _, _, disc_id, cdc = row[:9]
        disc_id = str(disc_id).strip()
        if not disc_id or not disc_id.isdigit():
            continue
        uid = int(disc_id)
        by_id[uid] = (
            uid,
            disc_name or f"user_{disc_id}",
            irl or None,
            cdc.strip() or None,
            lichess.strip() or None,
        )

    batch = list(by_id.values())
    if not batch:
        print("No rows with valid Discord IDs.")
        return

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS geri_users (
                    discord_user_id BIGINT PRIMARY KEY,
                    discord_name TEXT NOT NULL,
                    irl_name TEXT,
                    chesscom_username TEXT,
                    lichess_username TEXT
                )
                """
            )
            execute_values(
                cur,
                """
                INSERT INTO geri_users (
                    discord_user_id, discord_name, irl_name,
                    chesscom_username, lichess_username
                ) VALUES %s
                ON CONFLICT (discord_user_id) DO UPDATE SET
                    discord_name = EXCLUDED.discord_name,
                    irl_name = COALESCE(EXCLUDED.irl_name, geri_users.irl_name),
                    chesscom_username = COALESCE(EXCLUDED.chesscom_username, geri_users.chesscom_username),
                    lichess_username = COALESCE(EXCLUDED.lichess_username, geri_users.lichess_username)
                """,
                batch,
            )
        conn.commit()
        print(f"Upserted {len(batch)} user row(s).")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
