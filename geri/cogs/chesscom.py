import asyncio
import logging
import os
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from geri.repository.users import list_chesscom_usernames
from geri.services import chesscom_last_game, chesscom_leaderboard, chesscom_stats
from geri.services import user_registry
from geri.utils.chesscom_embeds import build_cdc_leaderboard_embed, build_cdc_profile_embed
from geri.utils.discord_safe import (
    defer_interaction_if_any,
    send_ctx_message,
    slash_reply_after_defer,
    user_facing_error,
)

log = logging.getLogger(__name__)


def _interaction_age_seconds(interaction: discord.Interaction) -> float:
    return max(
        0.0,
        (datetime.now(timezone.utc) - interaction.created_at).total_seconds(),
    )


def _is_unknown_interaction_error(exc: BaseException) -> bool:
    if isinstance(exc, discord.NotFound):
        return True
    return isinstance(exc, discord.HTTPException) and getattr(exc, "code", None) == 10062


async def _cdcprofile_fetch(
    caller_display_name: str,
    caller_user_id: int,
    lookup_name: str | None,
) -> tuple[str | None, discord.Embed | None]:
    record = user_registry.resolve_for_command(
        caller_display_name=caller_display_name,
        caller_user_id=caller_user_id,
        lookup_name=lookup_name,
    )
    if not record or not (record.get("chesscom_username") or "").strip():
        return (
            "No Chess.com username on file. Use `/addcdc` first (or `$addcdc`).",
            None,
        )
    cdc_name = record["chesscom_username"].strip()
    stats, profile = await asyncio.gather(
        asyncio.to_thread(chesscom_stats.chessdotcom_stats, cdc_name),
        asyncio.to_thread(chesscom_stats.fetch_profile_display, cdc_name),
    )
    return (None, build_cdc_profile_embed(stats, profile))


@app_commands.command(
    name="cdcprofile",
    description="Chess.com profile and ratings for a linked user.",
)
@app_commands.describe(
    name="Discord display name (optional); defaults to the invoking user",
)
async def slash_cdcprofile(interaction: discord.Interaction, name: str | None = None):
    """Slash-only: uses Interaction directly (hybrid Context is unreliable after defer)."""
    age = _interaction_age_seconds(interaction)
    if age > 2.5:
        log.warning(
            "slash cdcprofile: interaction is %.2fs old before defer (Discord allows ~3s to ack)",
            age,
        )

    try:
        await interaction.response.defer(ephemeral=False, thinking=True)
    except (discord.NotFound, discord.HTTPException) as e:
        if not _is_unknown_interaction_error(e):
            raise
        log.error(
            "slash cdcprofile: defer returned 10062 (age=%.2fs). "
            "Common causes: a second bot process using the same token, or the event loop "
            "was blocked so this handler started after the 3s interaction window.",
            age,
        )
        ch = interaction.channel
        if ch is not None:
            try:
                err, emb = await _cdcprofile_fetch(
                    str(interaction.user), interaction.user.id, name
                )
                if err:
                    await ch.send(f"{interaction.user.mention} {err}")
                else:
                    await ch.send(content=interaction.user.mention, embed=emb)
            except Exception:
                log.exception("slash cdcprofile channel fallback failed")
        return

    try:
        err, emb = await _cdcprofile_fetch(
            str(interaction.user), interaction.user.id, name
        )
        if err:
            await slash_reply_after_defer(interaction, content=err)
        else:
            await slash_reply_after_defer(interaction, embed=emb)
    except Exception as e:
        log.exception("slash cdcprofile failed")
        try:
            await slash_reply_after_defer(
                interaction,
                content=f"Could not load profile. {user_facing_error(e)}",
            )
        except Exception:
            log.exception("slash cdcprofile fallback reply failed")

_PERF_KEYS = (
    "streak",
    "bullet",
    "blitz",
    "rapid",
    "classical",
    "correspondence",
)
_PERF_LABELS = {
    "streak": "Puzzle Rush",
    "bullet": "Bullet",
    "blitz": "Blitz",
    "rapid": "Rapid",
    "classical": "Classical",
    "correspondence": "Daily chess",
}


class ChesscomCog(commands.Cog):
    """Chess.com hybrid commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        # Pure app command avoids hybrid Context + deferred interaction bugs (10062).
        self.bot.tree.add_command(slash_cdcprofile)

    async def cog_unload(self) -> None:
        try:
            self.bot.tree.remove_command(slash_cdcprofile.name)
        except Exception:
            pass

    @commands.command(name="cdcprofile")
    async def prefix_cdcprofile(self, ctx: commands.Context, *, name: str | None = None):
        """Chess.com profile and ratings ($cdcprofile)."""
        try:
            err, emb = await _cdcprofile_fetch(str(ctx.author), ctx.author.id, name)
            if err:
                await ctx.send(err)
            else:
                await ctx.send(embed=emb)
        except Exception as e:
            log.exception("prefix cdcprofile failed")
            await ctx.send(f"Could not load profile. {user_facing_error(e)}")

    @commands.hybrid_command(name="addcdc")
    @app_commands.describe(
        cdc_name="Your Chess.com username",
        irl_name="Real name (optional)",
    )
    async def addcdc(
        self,
        ctx: commands.Context,
        cdc_name: str,
        irl_name: str = None,
    ):
        """Save your Chess.com username for this Discord account."""
        await defer_interaction_if_any(ctx)
        try:
            updated = user_registry.upsert_caller_chesscom(
                discord_user_id=ctx.author.id,
                discord_display_name=str(ctx.author),
                chesscom_username=cdc_name,
                irl_name=irl_name,
            )
            await send_ctx_message(
                ctx,
                f"Chess.com username: **{updated['chesscom_username']}** saved. "
                f"Real name: **{updated['irl_name'] or '—'}**",
            )
        except Exception as e:
            log.exception("addcdc failed")
            await send_ctx_message(ctx, f"Could not save. {user_facing_error(e)}")

    @commands.hybrid_command(name="lastcdc")
    @app_commands.describe(
        name="Chess.com username (optional; defaults to your linked username)"
    )
    async def lastcdc(self, ctx: commands.Context, name: str = None):
        """Most recent finished Chess.com game in their archives (GIF)."""
        await defer_interaction_if_any(ctx)
        try:
            record = user_registry.resolve_for_command(
                caller_display_name=str(ctx.author),
                caller_user_id=ctx.author.id,
                lookup_name=None,
            )
            if name and name.strip():
                cdc_name = name.strip()
            elif record and (record.get("chesscom_username") or "").strip():
                cdc_name = record["chesscom_username"].strip()
            else:
                await send_ctx_message(
                    ctx,
                    "No Chess.com username. Use `/addcdc` or pass a Chess.com username (or `$addcdc`).",
                )
                return

            lastgame = await asyncio.to_thread(
                chesscom_last_game.fetch_last_game_dict, cdc_name
            )
            gif_path = os.path.join("temp", "chess.gif")
            await send_ctx_message(
                ctx,
                f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>",
            )
            await send_ctx_message(ctx, file=discord.File(gif_path))
        except Exception as e:
            log.exception("lastcdc failed")
            await send_ctx_message(
                ctx, f"Could not fetch game. {user_facing_error(e)}"
            )

    @commands.hybrid_command(name="cdcleaderboard")
    @app_commands.describe(
        perf="streak, bullet, blitz, rapid, classical, or correspondence"
    )
    async def cdcleaderboard(self, ctx: commands.Context, perf: str = "blitz"):
        """Leaderboard for Chess.com usernames registered in the database."""
        await defer_interaction_if_any(ctx)
        try:
            perf_key = (perf or "blitz").strip().lower()
            if perf_key not in _PERF_KEYS:
                await send_ctx_message(
                    ctx,
                    f"Invalid category. Use one of: {', '.join(_PERF_KEYS)}.",
                )
                return
            players = list_chesscom_usernames()
            if not players:
                await send_ctx_message(
                    ctx,
                    f"**{_PERF_LABELS[perf_key]}**\n"
                    "No Chess.com usernames in the database yet. Use `/addcdc` (or `$addcdc`).",
                )
                return
            rows = await chesscom_leaderboard.fetch_leaderboard_rows(perf_key)
            embed = build_cdc_leaderboard_embed(
                perf_key, _PERF_LABELS[perf_key], rows
            )
            await send_ctx_message(ctx, embed=embed)
        except Exception as e:
            log.exception("cdcleaderboard failed")
            await send_ctx_message(
                ctx, f"Could not build leaderboard. {user_facing_error(e)}"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ChesscomCog(bot))
