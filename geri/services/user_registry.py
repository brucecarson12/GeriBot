"""Resolve Discord users to stored registry rows."""

from typing import Any

from geri.repository import users as users_repo


def resolve_for_command(
    *,
    caller_display_name: str,
    caller_user_id: int,
    lookup_name: str | None,
) -> dict[str, Any] | None:
    """
    If lookup_name is set, find by stored discord_name (legacy sheet behavior).
    Otherwise find by caller's discord_user_id.
    """
    if lookup_name:
        name = lookup_name.strip()
        return users_repo.get_by_discord_name(name)
    return users_repo.get_by_discord_id(caller_user_id)


def upsert_caller_chesscom(
    *,
    discord_user_id: int,
    discord_display_name: str,
    chesscom_username: str,
    irl_name: str | None,
) -> dict[str, Any]:
    irl: str | None = None
    if irl_name and irl_name.strip():
        irl = irl_name.strip()
    return users_repo.upsert_chesscom(
        discord_user_id,
        discord_display_name,
        chesscom_username.strip(),
        irl,
    )
