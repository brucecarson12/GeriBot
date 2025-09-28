"""
Test commands for GeriBot - simplified version for debugging
"""
import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.embed_builder import EmbedBuilder


class TestCommands(commands.Cog):
    """Test commands for debugging"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ping", description="Test if the bot is responding")
    async def ping(self, ctx):
        """Test command to check if bot is responding"""
        embed = EmbedBuilder.create_success_embed(
            title="🏓 Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms"
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="hello", description="Say hello")
    async def hello(self, ctx):
        """Simple hello command"""
        embed = EmbedBuilder.create_info_embed(
            title="👋 Hello!",
            description="Hello from GeriBot! The bot is working correctly."
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="info", description="Get bot information")
    async def info(self, ctx):
        """Get bot information"""
        embed = EmbedBuilder.create_info_embed(
            title="ℹ️ Bot Information",
            description="GeriBot - Chess Tournament and Analysis Bot"
        )
        embed.add_field(name="Version", value="2.0.0", inline=True)
        embed.add_field(name="Status", value="✅ Online", inline=True)
        embed.add_field(name="Commands", value="Hybrid (Slash + Prefix)", inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(TestCommands(bot))
