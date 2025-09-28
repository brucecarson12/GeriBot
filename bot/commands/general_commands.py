"""
General commands for GeriBot
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import os
from bot.services.lichess_service import LichessService
from bot.services.chess_com_service import ChessComService
from bot.services.database_service import DatabaseService
from bot.services.puzzle_service import PuzzleService
from bot.utils.embed_builder import EmbedBuilder
from bot.utils.message_formatter import MessageFormatter


class GeneralCommands(commands.Cog):
    """General utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.lichess_service = LichessService()
        self.chess_com_service = ChessComService()
        self.database_service = DatabaseService()
        self.puzzle_service = PuzzleService()
    
    @commands.hybrid_command(name="hello", description="Say hello to GeriBot")
    async def hello(self, ctx):
        """Say hello to GeriBot"""
        embed = EmbedBuilder.create_success_embed(
            title="👋 Hello!",
            description="Hey! I'm GeriBot, your chess companion! Use `/geri` to learn more about me!"
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="geri", description="Learn about GeriBot")
    async def geri(self, ctx):
        """Learn about GeriBot and its namesake"""
        try:
            with open("data/Geri-intro.txt", "r") as introtext:
                txtinfo = introtext.read()
                embed = EmbedBuilder.create_chess_embed(
                    title="♟️ About GeriBot",
                    description=txtinfo
                )
                embed.add_field(
                    name="🎬 My Namesake", 
                    value="[Watch the inspiration](https://www.youtube.com/watch?v=uMVtpCPx8ow)",
                    inline=False
                )
                await ctx.send(embed=embed)
        except FileNotFoundError:
            embed = EmbedBuilder.create_error_embed(
                title="❌ File Not Found",
                description="Sorry, I couldn't find my introduction file."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Error",
                description=f"An error occurred: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="resources", description="Get helpful chess resources")
    async def resources(self, ctx):
        """Shares some helpful resources for improving at chess!"""
        try:
            with open("data/resources.txt", "r") as resourcetext:
                txt = resourcetext.read()
                embed = EmbedBuilder.create_info_embed(
                    title="📚 Chess Resources",
                    description="Here are some helpful resources for improving your chess game!"
                )
                # Split the text into sections for better formatting
                sections = txt.split('\n\n')
                for section in sections:
                    if section.strip():
                        lines = section.strip().split('\n')
                        if lines:
                            title = lines[0].replace('__', '').replace(':', '')
                            content = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
                            embed.add_field(name=title, value=content, inline=False)
                await ctx.send(embed=embed)
        except FileNotFoundError:
            embed = EmbedBuilder.create_error_embed(
                title="❌ File Not Found",
                description="Sorry, I couldn't find the resources file."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Error",
                description=f"An error occurred: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="puzzle", description="Get a random chess puzzle")
    async def puzzle(self, ctx):
        """Gives a random puzzle to the chat"""
        try:
            filename2, clue, title, fentxt, solution = self.puzzle_service.get_random_puzzle()
            
            # Create puzzle embed
            puzzle_data = {
                'clue': clue,
                'title': title,
                'solution': solution
            }
            embed = EmbedBuilder.create_puzzle_embed(puzzle_data)
            
            await ctx.send(embed=embed)
            await ctx.send(file=discord.File(filename2))
            os.remove(filename2)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Puzzle Error",
                description=f"An error occurred while generating the puzzle: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="challenge", description="Create an open Lichess challenge")
    @app_commands.describe(limit="Time limit in minutes (default: 5)", inc="Time increment in seconds (default: 0)")
    async def challenge(self, ctx, limit: int = 5, inc: int = 0):
        """Creates an open challenge for 2 players to join"""
        try:
            challenge = self.lichess_service.create_challenge(limit=limit, increment=inc)
            embed = EmbedBuilder.create_success_embed(
                title="🎯 Challenge Created!",
                description=f"**Time Control:** {limit} minutes + {inc} seconds increment"
            )
            embed.add_field(
                name="🔗 Challenge Link", 
                value=f"[Join Challenge]({challenge['url']})",
                inline=False
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Challenge Error",
                description=f"An error occurred while creating the challenge: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="onlinenow", description="List players currently online on Lichess")
    async def onlinenow(self, ctx):
        """Lists the current players I see online now"""
        try:
            players = self.database_service.get_lichess_players()
            onlinemessage = self.lichess_service.get_online_players(players)
            embed = EmbedBuilder.create_lichess_embed(
                title="🟢 Online Players",
                description=onlinemessage
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Online Check Error",
                description=f"An error occurred while checking online players: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="performance", description="Calculate performance rating from tournament results")
    @app_commands.describe(score="Your score (wins)", ratings="Opponent ratings (space-separated)")
    async def performance(self, ctx, score: int = 0, ratings: str = ""):
        """Calculates Performance Rating from a tournament based on score and opponent ratings"""
        try:
            if not ratings:
                embed = EmbedBuilder.create_warning_embed(
                    title="⚠️ Missing Parameters",
                    description="Please provide opponent ratings.\n**Example:** `/performance 3 1614 1195 1964 1900`"
                )
                await ctx.send(embed=embed)
                return
            
            args = [int(a) for a in ratings.split()]
            perfTxt = self._calculate_performance_rating(score, args)
            
            # Create a formatted embed for performance rating
            embed = EmbedBuilder.create_info_embed(
                title="📊 Performance Rating Calculation",
                description=perfTxt
            )
            await ctx.send(embed=embed)
        except ValueError:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Invalid Input",
                description="Please provide valid numbers for score and ratings."
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                title="❌ Calculation Error",
                description=f"An error occurred while calculating performance rating: {e}"
            )
            await ctx.send(embed=embed)
    
    def _calculate_performance_rating(self, your_score: int, opponent_ratings: list) -> str:
        """Calculate performance rating from score and opponent ratings"""
        if your_score > len(opponent_ratings):
            return "Hmm, you won more games than you played..."
        elif your_score < 0:
            return "It couldn't have been that bad!"
        elif your_score == len(opponent_ratings):
            performance_output = "Excellent Tournament!\n"
        else:
            performance_output = ""
        
        # Calculate performance rating
        num_games = len(opponent_ratings)
        avg_opponent_rating = int(round(sum(opponent_ratings) / len(opponent_ratings), 0))
        perf_rating = int(round(avg_opponent_rating + (800 * (your_score / len(opponent_ratings) - 0.5)), 0))
        
        norm_txt = self._check_for_norms(your_score, opponent_ratings)
        
        performance_output += f""" You played {num_games} games and your opponents' average rating was {avg_opponent_rating}.\nYour performance rating was {perf_rating}.\n{norm_txt}"""
        
        return performance_output
    
    def _check_for_norms(self, your_score: int, opponent_ratings: list) -> str:
        """Check for US Chess norms earned"""
        if len(opponent_ratings) < 4:
            return "Norm Earned | A Norm requires at least 4 games"
        else:
            norm_award = "None"
        
        levels = {
            'Category 1': 1200, 'Category 2': 1400, 'Category 3': 1600, 'Category 4': 1800,
            'Candidate Master(rating dependent)': 2000, 
            'Life Master(rating dependent)': 2200, 
            'Senior Life Master(rating dependent)': 2400
        }
        
        for i in levels.values():
            points = 0
            for opp in opponent_ratings:
                difference = i - opp
                point_calc = 1
                if difference <= -400:
                    point_calc = 0
                elif -400 < difference <= 0:
                    point_calc = .5 + difference / 800 
                elif 1 <= difference <= 200:
                    point_calc = .5 + difference / 400
                points += point_calc
            if your_score - points > 1:
                norm_award = [txt for txt in levels if levels[txt] == i][0]
            if your_score - points <= 1:
                break
        
        norm_txt = f"Norm Earned: {norm_award}\nMore info on Norms can be found here: http://www.glicko.net/ratings/titles.pdf" 
        
        return norm_txt


async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
