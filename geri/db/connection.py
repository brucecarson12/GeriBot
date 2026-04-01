"""Postgres connection pool and schema initialization."""

from contextlib import contextmanager
from typing import Generator

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from geri.config import get_database_url

_pool: SimpleConnectionPool | None = None

# Named geri_users to avoid clashing with an existing public.users table from other apps.
SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS geri_users (
        discord_user_id BIGINT PRIMARY KEY,
        discord_name TEXT NOT NULL,
        irl_name TEXT,
        chesscom_username TEXT,
        lichess_username TEXT
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_geri_users_discord_name ON geri_users (discord_name)
    """,
]


def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(1, 10, dsn=get_database_url())


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


def init_db() -> None:
    """Create tables if missing. Safe to call on every startup."""
    init_pool()
    assert _pool is not None
    conn = _pool.getconn()
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            for stmt in SCHEMA_STATEMENTS:
                cur.execute(stmt)
    finally:
        _pool.putconn(conn)


@contextmanager
def get_connection() -> Generator:
    init_pool()
    assert _pool is not None
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def dict_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)
