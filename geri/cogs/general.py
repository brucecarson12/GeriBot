import os

import discord
from discord.ext import commands

from geri.utils.discord_safe import defer_interaction_if_any, send_ctx_message


class GeneralCog(commands.Cog):
    """Public help and greeting."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="hello")
    async def hello(self, ctx: commands.Context):
        """Say hello to Geri."""
        await send_ctx_message(
            ctx, "Hey! Use `/geri` for Chess.com commands (or `$geri`)."
        )

    @commands.hybrid_command(name="geri")
    async def geri(self, ctx: commands.Context):
        """Show what Geri can do (Chess.com)."""
        await defer_interaction_if_any(ctx)
        path = os.path.join("data", "Geri-intro.txt")
        with open(path, encoding="utf-8") as introtext:
            txtinfo = introtext.read()
        embed = discord.Embed(
            description="[My namesake.](https://www.youtube.com/watch?v=uMVtpCPx8ow)"
        )
        await send_ctx_message(ctx, content=txtinfo, embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))
