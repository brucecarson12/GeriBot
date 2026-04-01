-- Geri user registry (same DDL as geri.db.connection.init_db).
-- Table is geri_users so it does not collide with other apps' public.users.
-- Run manually only if you prefer not to rely on the bot’s first startup, e.g.:
--   heroku pg:psql -a YOUR_APP -f geri/db/schema.sql

CREATE TABLE IF NOT EXISTS geri_users (
    discord_user_id BIGINT PRIMARY KEY,
    discord_name TEXT NOT NULL,
    irl_name TEXT,
    chesscom_username TEXT,
    lichess_username TEXT
);

CREATE INDEX IF NOT EXISTS idx_geri_users_discord_name ON geri_users (discord_name);
