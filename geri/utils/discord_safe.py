"""Keep outbound Discord text within limits."""

from __future__ import annotations

from typing import Any

import discord
from discord.ext import commands

DISCORD_CONTENT_MAX = 2000
SAFE_MAX = 1900


async def defer_interaction_if_any(ctx: commands.Context) -> None:
    """Acknowledge slash within 3s; no-op for prefix. Public (non-ephemeral) followups."""
    inter = ctx.interaction
    if inter is None or inter.response.is_done():
        return
    await inter.response.defer(ephemeral=False, thinking=True)


def _interaction_unknown(exc: BaseException) -> bool:
    if isinstance(exc, discord.NotFound):
        return True
    return isinstance(exc, discord.HTTPException) and getattr(exc, "code", None) == 10062


async def slash_reply_after_defer(
    interaction: discord.Interaction,
    *,
    content: str | None = None,
    embed: discord.Embed | None = None,
) -> None:
    """
    After interaction.response.defer(..., thinking=True), replace the placeholder with
    the final message. If edit_original_response fails (e.g. 10062), fall back to channel.send.
    """
    edit_kw: dict[str, Any] = {}
    if content is not None:
        edit_kw["content"] = content
    if embed is not None:
        edit_kw["embed"] = embed
    if not edit_kw:
        raise ValueError("slash_reply_after_defer requires content and/or embed")
    try:
        await interaction.edit_original_response(**edit_kw)
    except (discord.HTTPException, discord.NotFound) as e:
        if not _interaction_unknown(e):
            raise
        ch = interaction.channel
        if ch is None:
            raise
        await ch.send(content=content, embed=embed)


def _normalize_send_kwargs(
    args: tuple[Any, ...], kwargs: dict[str, Any]
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """`send_ctx_message(ctx, "hi")` → content= keyword for consistent routing."""
    if len(args) == 1 and isinstance(args[0], str) and "content" not in kwargs:
        return (), {**kwargs, "content": args[0]}
    if len(args) == 1 and isinstance(args[0], discord.Embed) and "embed" not in kwargs:
        return (), {**kwargs, "embed": args[0]}
    return args, kwargs


async def send_ctx_message(
    ctx: commands.Context, *args: Any, **kwargs: Any
) -> discord.Message | None:
    """
    Reply for prefix or slash. After defer(), prefer editing the deferred / "thinking"
    message via edit_original_response — followup.send often hits 10062 Unknown interaction
    when the token/webhook path misbehaves after slow work.
    """
    args, kwargs = _normalize_send_kwargs(args, dict(kwargs))

    inter = ctx.interaction
    if inter is None:
        return await ctx.send(*args, **kwargs)

    if not inter.response.is_done():
        return await inter.response.send_message(*args, **kwargs)

    file = kwargs.get("file")
    files = kwargs.get("files")
    content = kwargs.get("content")
    embed = kwargs.get("embed")
    embeds = kwargs.get("embeds")
    allowed_mentions = kwargs.get("allowed_mentions")

    # No attachment: patch the original deferred response (recommended for defer+embed/text).
    if file is None and files is None:
        edit_kw: dict[str, Any] = {}
        if content is not None:
            edit_kw["content"] = content
        if embed is not None:
            edit_kw["embed"] = embed
        if embeds is not None:
            edit_kw["embeds"] = embeds
        if allowed_mentions is not None:
            edit_kw["allowed_mentions"] = allowed_mentions
        if edit_kw:
            try:
                return await inter.edit_original_response(**edit_kw)
            except (discord.HTTPException, discord.NotFound) as e:
                if not _interaction_unknown(e):
                    raise

    try:
        return await inter.followup.send(*args, **kwargs)
    except Exception as e:
        if _interaction_unknown(e) and ctx.channel is not None:
            try:
                return await ctx.channel.send(*args, **kwargs)
            except Exception:
                pass
        raise


def clip_message(text: str, max_len: int = SAFE_MAX) -> str:
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def user_facing_error(exc: BaseException) -> str:
    """Short message for users; full detail stays in logs."""
    name = type(exc).__name__
    try:
        from chessdotcom.errors import ChessDotComClientError

        if isinstance(exc, ChessDotComClientError):
            body = (exc.text or "")[:2000]
            if (
                "Just a moment" in body
                or "__cf_chl" in body
                or "challenge-platform" in body
                or "Sorry, you have been blocked" in body
                or "Attention Required!" in body
                or "cf-error-details" in body
            ):
                return (
                    f"{name} ({exc.status_code}): Chess.com / Cloudflare blocked this request "
                    "(not a bad username). Try: set CHESSCOM_USER_AGENT in .env with a clear "
                    "name + contact; run the bot from another network if you’re on VPN/datacenter; "
                    "wait and retry. The public API cannot pass browser CAPTCHAs."
                )
            return clip_message(
                f"{name} (HTTP {exc.status_code}) from Chess.com API. "
                f"If the player exists, try again; otherwise check the username."
            )
    except Exception:
        pass
    raw = str(exc).strip()
    if len(raw) > 300:
        raw = raw[:297] + "…"
    return clip_message(f"{name}: {raw}" if raw else name)
