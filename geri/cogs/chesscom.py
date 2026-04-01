import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from geri.services import chesscom_last_game, chesscom_leaderboard, chesscom_stats
from geri.services import user_registry
from geri.utils.discord_safe import clip_message, user_facing_error

log = logging.getLogger(__name__)


class ChesscomCog(commands.Cog):
    """Chess.com hybrid commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _defer_if_needed(self, ctx: commands.Context) -> None:
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.defer()

    @commands.hybrid_command(name="cdcprofile")
    @app_commands.describe(
        name="Discord display name (optional; defaults to the invoking user)"
    )
    async def cdcprofile(self, ctx: commands.Context, name: str = None):
        """Chess.com profile and ratings for a linked user."""
        await self._defer_if_needed(ctx)
        try:
            record = user_registry.resolve_for_command(
                caller_display_name=str(ctx.author),
                caller_user_id=ctx.author.id,
                lookup_name=name,
            )
            if not record or not (record.get("chesscom_username") or "").strip():
                await ctx.send(
                    "No Chess.com username on file. Use `/addcdc` or `$addcdc` first."
                )
                return
            cdc_name = record["chesscom_username"].strip()
            ratings = chesscom_stats.chessdotcom_stats(cdc_name)
            msg = f"{ratings['txt']} \n<https://www.chess.com/member/{cdc_name}>"
            await ctx.send(clip_message(msg))
        except Exception as e:
            log.exception("cdcprofile failed")
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
        try:
            updated = user_registry.upsert_caller_chesscom(
                discord_user_id=ctx.author.id,
                discord_display_name=str(ctx.author),
                chesscom_username=cdc_name,
                irl_name=irl_name,
            )
            await ctx.send(
                f"Chess.com username: **{updated['chesscom_username']}** saved. "
                f"Real name: **{updated['irl_name'] or '—'}**"
            )
        except Exception as e:
            log.exception("addcdc failed")
            await ctx.send(f"Could not save. {user_facing_error(e)}")

    @commands.hybrid_command(name="lastcdc")
    @app_commands.describe(
        name="Chess.com username (optional; defaults to your linked username)"
    )
    async def lastcdc(self, ctx: commands.Context, name: str = None):
        """Most recent finished Chess.com game in their archives (GIF)."""
        await self._defer_if_needed(ctx)
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
                await ctx.send(
                    "No Chess.com username. Use `$addcdc` / `/addcdc` or pass a username."
                )
                return

            lastgame = chesscom_last_game.fetch_last_game_dict(cdc_name)
            gif_path = os.path.join("temp", "chess.gif")
            await ctx.send(
                f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>"
            )
            await ctx.send(file=discord.File(gif_path))
        except Exception as e:
            log.exception("lastcdc failed")
            await ctx.send(f"Could not fetch game. {user_facing_error(e)}")

    @commands.hybrid_command(name="cdcleaderboard")
    @app_commands.describe(
        perf="streak, bullet, blitz, rapid, classical, or correspondence"
    )
    async def cdcleaderboard(self, ctx: commands.Context, perf: str = "blitz"):
        """Leaderboard for Chess.com usernames registered in the database."""
        await self._defer_if_needed(ctx)
        try:
            text = chesscom_leaderboard.format_cdc_leaderboard(perf)
            await ctx.send(clip_message(text))
        except Exception as e:
            log.exception("cdcleaderboard failed")
            await ctx.send(f"Could not build leaderboard. {user_facing_error(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChesscomCog(bot))
