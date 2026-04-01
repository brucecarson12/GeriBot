# GeriBot

Discord bot focused on **Chess.com**: link accounts, show ratings, last game (with GIF), and a leaderboard for members stored in the database.

## Setup

- **Python 3.12+** recommended ([runtime.txt](runtime.txt)).
- **Environment variables** (e.g. `.env`): `DiscToken`, `DATABASE_URL` (Heroku Postgres URL is fine).
- Optional: `TEST_GUILD_ID` for fast slash-command sync to one guild during development; `DEBUG=1` for verbose logs.
- Install: `pip install -r requirements.txt`
- Run: `python main.py` (see [Procfile](Procfile) for Heroku).

## One-time migration from Google Sheets

If you still have the old `Chess_Tourney` sheet and `google-credentials.json`:

```bash
pip install gspread google-auth
python scripts/migrate_sheet_to_pg.py
```

## Layout

- [main.py](main.py) — bot entry, extension loading, sync.
- [geri/cogs/](geri/cogs/) — Discord commands.
- [geri/services/](geri/services/) — Chess.com API and orchestration.
- [geri/repository/](geri/repository/) — Postgres access for table **`geri_users`** (avoids clashing with other apps’ `users`; includes unused-for-now `lichess_username`).

Tournament / Lichess command code has been removed from the active app; legacy folders may still exist under `_old/` or nested copies and are not loaded.
