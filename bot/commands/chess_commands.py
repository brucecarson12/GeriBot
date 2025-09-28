"""
Chess.com related commands for GeriBot
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.services.chess_com_service import ChessComService
from bot.services.database_service import DatabaseService
from bot.utils.embed_builder import EmbedBuilder
from bot.utils.message_formatter import MessageFormatter


class ChessCommands(commands.Cog):
    """Chess.com related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.chess_com_service = ChessComService()
        self.database_service = DatabaseService()
    
    @commands.hybrid_command(name="profile", description="Get Chess.com and Lichess profiles")
    @app_commands.describe(name="Discord username (optional, defaults to you)")
    async def profile(self, ctx, name: Optional[str] = None):
        """Grabs chess.com and lichess profiles of the name given or the one who calls the command"""
        try:
            from bot.services.lichess_service import LichessService
            lichess_service = LichessService()
            
            Name = str(ctx.author) if not name else name.strip()
            User = self.database_service.update_discord_user(Name)
            ratings = self.chess_com_service.get_player_stats(User['cdc'])
            liratings = lichess_service.get_user_ratings(User['lichess'])
            
            # Create combined profile embed
            embed = EmbedBuilder.create_info_embed(
                title="👤 Player Profile",
                description=f"**Discord:** {Name}"
            )
            
            # Add Chess.com section
            embed.add_field(
                name="🏆 Chess.com",
                value=f"**Username:** {User['cdc']}\n{ratings['txt']}\n[View Profile](https://www.chess.com/member/{User['cdc']})",
                inline=False
            )
            
            # Add Lichess section
            embed.add_field(
                name="♟️ Lichess",
                value=f"**Username:** {User['lichess']}\n{liratings['txt']}\n[View Profile](https://lichess.org/@/{User['lichess']})",
                inline=False
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Profile Not Found",
                description="Hmm, I couldn't find your name. Use the `/addcdc` command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command (Ex. `/cdcprofile plsBnyce`)."
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="cdcprofile", description="Get Chess.com profile and stats")
    @app_commands.describe(name="Discord username (optional, defaults to you)")
    async def cdcprofile(self, ctx, name: Optional[str] = None):
        """Grabs a chess.com profile and stats"""
        try:
            Name = str(ctx.author) if not name else name.strip()
            User = self.database_service.update_discord_user(Name)
            ratings = self.chess_com_service.get_player_stats(User['cdc'])
            
            embed = EmbedBuilder.create_chess_com_embed(
                title=f"🏆 Chess.com Profile: {User['cdc']}",
                description=ratings['txt']
            )
            embed.add_field(
                name="🔗 Profile Link",
                value=f"[View Profile](https://www.chess.com/member/{User['cdc']})",
                inline=False
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Profile Not Found",
                description="Hmm, I couldn't find your name. Use the `/addcdc` command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command (Ex. `/cdcprofile plsBnyce`)."
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="addcdc", description="Add your Chess.com username")
    @app_commands.describe(cdcname="Your Chess.com username", irlname="Your real name (optional)")
    async def addcdc(self, ctx, cdcname: str, irlname: Optional[str] = None):
        """Add your chess.com username to your profile"""
        try:
            member = str(ctx.author)
            memberid = ctx.author.id
            Sheetinfo = self.database_service.update_discord_user(member, memberid, IRLname=irlname, cdcname=cdcname)
            
            embed = EmbedBuilder.create_success_embed(
                title="✅ Chess.com Username Added!",
                description=f"**Username:** {Sheetinfo['cdc']}\n**Real Name:** {Sheetinfo['IRLname']}"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Registration Error",
                description="Hmm, I don't see you in my records. Please make sure to enter a Chess.com Username after your command. (Ex. `/addcdc username`)"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="lastcdc", description="Get your last Chess.com game")
    @app_commands.describe(name="Chess.com username (optional, defaults to your registered name)")
    async def lastcdc(self, ctx, name: Optional[str] = None):
        """Grabs your last chess.com game if Geri has your username"""
        try:
            Name = str(ctx.author)
            memberId = ctx.author.id
            User = self.database_service.update_discord_user(Name, memberId)
            cdcname = User['cdc'] if name is None else name.strip()
            lastgame = self.chess_com_service.get_last_game(cdcname)
            await ctx.send(f"{lastgame['result']}\n{lastgame['vstxt']}\n<{lastgame['url']}>")
            await ctx.send(file=discord.File("temp/chess.gif"))
        except Exception as e:
            await ctx.send(f"Still testing this one. Bear with me.")
    
    @commands.hybrid_command(name="cdcleaderboard", description="Get Chess.com leaderboard")
    @app_commands.describe(perf="Performance type (blitz, bullet, rapid, classical, correspondence, streak)")
    async def cdcleaderboard(self, ctx, perf: str = 'blitz'):
        """Chess.com Leaderboard generator. Defaults to Blitz"""
        try:
            # This would need to be implemented with proper database integration
            await ctx.send(f"Chess.com {perf.title()} leaderboard functionality needs database integration")
        except Exception as e:
            await ctx.send(f"An error occurred while generating the leaderboard: {e}")


async def setup(bot):
    await bot.add_cog(ChessCommands(bot))
