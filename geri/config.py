"""Environment and runtime configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def get_database_url() -> str:
    raw = os.getenv("DATABASE_URL")
    if not raw:
        raise RuntimeError("DATABASE_URL is not set (required for Heroku Postgres).")
    return normalize_database_url(raw)


def get_discord_token() -> str:
    token = os.getenv("DiscToken")
    if not token:
        raise RuntimeError("DiscToken is not set.")
    return token


def get_test_guild_id() -> int | None:
    raw = os.getenv("TEST_GUILD_ID")
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def debug_mode() -> bool:
    return os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
