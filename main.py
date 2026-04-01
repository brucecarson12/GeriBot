"""
Geri — Discord bot for Chess.com (hybrid commands).
"""

from __future__ import annotations

import logging
import sys

import discord
import nest_asyncio
from discord import app_commands
from discord.ext import commands

from geri.config import debug_mode, get_discord_token, get_test_guild_id
from geri.db.connection import init_db
from geri.services.chesscom_bootstrap import ensure_chesscom_configured
from geri.utils.discord_safe import clip_message, user_facing_error

nest_asyncio.apply()

logging.basicConfig(
    level=logging.DEBUG if debug_mode() else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("geri.main")


class GeriBot(commands.Bot):
    async def setup_hook(self) -> None:
        init_db()
        ensure_chesscom_configured()
        extensions = (
            "geri.cogs.general",
            "geri.cogs.chesscom",
            "geri.cogs.admin",
        )
        for ext in extensions:
            await self.load_extension(ext)
            log.info("Loaded extension %s", ext)

        guild_id = get_test_guild_id()
        if guild_id:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info("Synced %d command(s) to guild %s", len(synced), guild_id)
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global command(s)", len(synced))


def build_bot() -> GeriBot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    return GeriBot(command_prefix="$", intents=intents)


bot = build_bot()


@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="$geri / /geri"
        )
    )


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Not enough information for that command.")
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CommandInvokeError) and error.original:
        log.exception("Prefix command error", exc_info=error.original)
        try:
            await ctx.send(
                clip_message(f"Something went wrong. {user_facing_error(error.original)}")
            )
        except Exception:
            pass
        return
    log.exception("Prefix command error: %s", error)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    log.exception(
        "Slash error in %s: %s",
        interaction.command.name if interaction.command else "?",
        error,
    )
    orig = getattr(error, "original", None)
    msg = user_facing_error(orig) if orig else str(error)
    msg = clip_message(f"Error: {msg}", max_len=900)
    if interaction.response.is_done():
        try:
            await interaction.followup.send(f"Error: {msg}", ephemeral=True)
        except Exception:
            pass
    else:
        try:
            await interaction.response.send_message(f"Error: {msg}", ephemeral=True)
        except Exception:
            pass


def main() -> None:
    try:
        token = get_discord_token()
    except RuntimeError as e:
        log.error("%s", e)
        sys.exit(1)
    bot.run(token)


if __name__ == "__main__":
    main()
