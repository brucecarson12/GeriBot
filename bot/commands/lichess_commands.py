"""
Lichess related commands for GeriBot
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import os
import requests
from bot.services.lichess_service import LichessService
from bot.services.database_service import DatabaseService
from bot.services.puzzle_service import PuzzleService
from bot.utils.embed_builder import EmbedBuilder
from bot.utils.message_formatter import MessageFormatter


class LichessCommands(commands.Cog):
    """Lichess related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.lichess_service = LichessService()
        self.database_service = DatabaseService()
        self.puzzle_service = PuzzleService()
    
    @commands.hybrid_command(name="lipuzzle", description="Get a random Lichess puzzle")
    async def lipuzzle(self, ctx):
        """Gives a random puzzle from lichess"""
        try:
            puzzle = self.puzzle_service.get_lichess_puzzle()
            
            # Create puzzle embed
            puzzle_data = {
                'rating': puzzle['rating'],
                'themes': puzzle['themes'],
                'solution': puzzle['solution'],
                'toPlay': puzzle['toPlay']
            }
            embed = EmbedBuilder.create_puzzle_embed(puzzle_data)
            embed.add_field(
                name="🎮 Game Link",
                value=f"[View Game]({puzzle['gameurl']})",
                inline=False
            )
            
            await ctx.send(embed=embed)
            await ctx.send(file=discord.File(puzzle['img']))
            os.remove(puzzle['img'])
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Puzzle Error",
                description=f"An error occurred while generating the puzzle: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="liprofile", description="Get a Lichess profile")
    @app_commands.describe(name="Lichess username (optional, defaults to your registered name)")
    async def liprofile(self, ctx, name: Optional[str] = None):
        """Grabs a lichess profile (case sensitive usernames!)"""
        try:
            if name:
                name = name.strip()
            else:
                User = self.database_service.update_discord_user(str(ctx.author))
                name = User['lichess']
            ratings = self.lichess_service.get_user_ratings(name)
            await ctx.send(f"{ratings['txt']}\n<https://lichess.org/@/{name}> \n<https://lichess.org/insights/{name}/result/opening>")
        except Exception as e:
            await ctx.send(f"Hmm, I couldn't find your name. Use the $addli command to add a username to my records. If you're looking for another player then make sure you've typed a username behind your command (Ex. $liprofile bnyce).")
    
    @commands.hybrid_command(name="findli", description="Find the most recent game between two Lichess users")
    @app_commands.describe(user1="First Lichess username", user2="Second Lichess username")
    async def findli(self, ctx, user1: str, user2: str):
        """Finds the most recently started game between 2 lichess users"""
        try:
            gameinfo = self.lichess_service.find_game_between_users(user1, user2)
            infotext = "Most Recent Game"
            if gameinfo['live']:
                infotext = "Live Game"
            await ctx.send(f"{infotext}: <{gameinfo['link']}> \n{gameinfo['opening']}")
            with open('game.gif', 'wb') as f:
                f.write(requests.get(gameinfo['giflink']).content)
            await ctx.send(file=discord.File('game.gif'))
            os.remove('game.gif')
        except Exception as e:
            await ctx.send(f"An error occurred while finding the game: {e}")
    
    @commands.hybrid_command(name="lastli", description="Get your last Lichess game")
    @app_commands.describe(skipno="Number of games to skip (default: 0)")
    async def lastli(self, ctx, skipno: int = 0):
        """This command grabs your last lichess game (based on start date)"""
        try:
            member = str(ctx.author)
            memberid = ctx.author.id
            Sheetinfo = self.database_service.update_discord_user(member, memberid)
            lastone = self.lichess_service.get_last_game(Sheetinfo['lichess'], skipno)

            result = str()
            if lastone['status'] == 'draw':
                result = "\nResult: 1/2-1/2"
            elif 'winner' in lastone.keys():
                if lastone['winner'] == 'white':
                    result = "\nResult: 1-0"
                elif lastone['winner'] == 'black':
                    result = "\nResult: 0-1"
            analysis = str()
            if lastone['analysis'] is not None:
                analysis = (f"Average Centipawn Loss: {lastone['analysis']['acpl']} \nInaccuracies({lastone['analysis']['inaccuracy']}): {', '.join(lastone['badmoves']['inaccuracy'])} \nMistakes({lastone['analysis']['mistake']}): {', '.join(lastone['badmoves']['mistake'])} \nBlunders({lastone['analysis']['blunder']}): {', '.join(lastone['badmoves']['blunder'])}")
            await ctx.send(f"{lastone['perf']}: <{lastone['link']}> \n{lastone['opening']}\n{analysis}{result} [{lastone['end']}]")
            await ctx.send(lastone['gif'])
        except Exception as e:
            await ctx.send(f"An error occurred while getting your last game: {e}")
    
    @commands.hybrid_command(name="addli", description="Add your Lichess username")
    @app_commands.describe(lichessname="Your Lichess username", irlname="Your real name (optional)")
    async def addli(self, ctx, lichessname: str, irlname: Optional[str] = None):
        """Add your lichess username to your profile"""
        try:
            member = str(ctx.author)
            memberid = ctx.author.id
            if irlname:
                Sheetinfo = self.database_service.add_lichess_user(lichessname.strip(), member, memberid, irlname.strip())
            else:
                Sheetinfo = self.database_service.add_lichess_user(lichessname.strip(), member, memberid, irlname)

            await ctx.send(f"lichess username: {Sheetinfo['lichess']} added to your info.")
        except Exception as e:
            await ctx.send(f"An error occurred while adding your Lichess username: {e}")
    
    @commands.hybrid_command(name="lileaderboard", description="Get Lichess leaderboard")
    @app_commands.describe(perf="Performance type (blitz, bullet, rapid, classical, correspondence, streak)")
    async def lileaderboard(self, ctx, perf: str = 'blitz'):
        """Lichess Leaderboard generator. Defaults to Blitz"""
        try:
            players = self.database_service.get_lichess_players()
            li_derboard = self.lichess_service.get_leaderboard(players, perf)
            await ctx.send(f"{li_derboard}")
        except Exception as e:
            await ctx.send(f"An error occurred while generating the leaderboard: {e}")
    


async def setup(bot):
    await bot.add_cog(LichessCommands(bot))
