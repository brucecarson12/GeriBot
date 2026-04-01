import discord
from discord.ext import commands

from geri.config import get_test_guild_id
from geri.repository.users import upsert_chesscom


def _admin_denied_message() -> str:
    return "You need administrator permissions to use this command."


def _is_guild_admin(ctx: commands.Context) -> bool:
    m = ctx.author
    return isinstance(m, discord.Member) and m.guild_permissions.administrator


class AdminCog(commands.Cog):
    """Prefix-only maintenance commands (hidden from slash tree and default help)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="test", with_app_command=False, hidden=True)
    async def test(self, ctx: commands.Context):
        """Smoke test (prefix only)."""
        await ctx.send("Geri is up. Hybrid user commands use `/` or `$`.")

    @commands.hybrid_command(name="adminhelp", with_app_command=False, hidden=True)
    async def adminhelp(self, ctx: commands.Context):
        """List prefix-only admin commands (not shown in default help)."""
        if ctx.guild is None:
            await ctx.send("Use this command in a server.")
            return
        if not _is_guild_admin(ctx):
            await ctx.send(_admin_denied_message())
            return
        body = (
            "**Admin commands** (prefix `$` only)\n"
            "• `$test` — smoke test\n"
            "• `$sync` — push slash commands to Discord "
            "(test guild if `TEST_GUILD_ID` is set, else global)\n"
            "• `$addplayer @member chesscom_username` — register or update a user in the DB "
            "(optional extra words: IRL name)\n"
            "• `$adminhelp` — this list"
        )
        await ctx.send(body)

    @commands.hybrid_command(name="sync", with_app_command=False, hidden=True)
    async def sync(self, ctx: commands.Context):
        """Re-register slash commands with Discord (admin only, prefix only)."""
        if ctx.guild is None:
            await ctx.send("Use this command in a server.")
            return
        if not _is_guild_admin(ctx):
            await ctx.send(_admin_denied_message())
            return
        try:
            guild_id = get_test_guild_id()
            if guild_id:
                guild = discord.Object(id=guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                await ctx.send(f"Synced {len(synced)} command(s) to test guild {guild_id}.")
            else:
                synced = await self.bot.tree.sync()
                await ctx.send(f"Synced {len(synced)} global command(s).")
        except Exception as e:
            await ctx.send(f"Failed to sync: {e}")

    @commands.hybrid_command(name="addplayer", with_app_command=False, hidden=True)
    async def addplayer(
        self,
        ctx: commands.Context,
        member: discord.Member,
        chesscom_username: str,
        *irl_parts: str,
    ):
        """Upsert a Discord member and Chess.com username into `geri_users` (admin only)."""
        if ctx.guild is None:
            await ctx.send("Use this command in a server.")
            return
        if not _is_guild_admin(ctx):
            await ctx.send(_admin_denied_message())
            return
        if not chesscom_username.strip():
            await ctx.send("Chess.com username is required.")
            return
        irl_name = " ".join(irl_parts).strip() or None
        rec = upsert_chesscom(
            discord_user_id=member.id,
            discord_name=member.display_name,
            chesscom_username=chesscom_username,
            irl_name=irl_name,
        )
        cc = rec["chesscom_username"]
        await ctx.send(
            f"Saved **{member.display_name}** → Chess.com `{cc}`"
            + (f" (IRL: {rec['irl_name']})" if rec.get("irl_name") else "")
            + "."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
