"""
Discord embed builder utility for GeriBot
"""
import discord
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmbedBuilder:
    """Utility class for building Discord embeds with consistent styling"""
    
    # Color constants
    SUCCESS_COLOR = 0x00ff00      # Green
    ERROR_COLOR = 0xff0000         # Red
    WARNING_COLOR = 0xffaa00      # Orange
    INFO_COLOR = 0x0099ff          # Blue
    CHESS_COLOR = 0x8b4513        # Brown (chess board color)
    LICHESS_COLOR = 0x000000      # Black (Lichess theme)
    CHESS_COM_COLOR = 0x1e40af    # Blue (Chess.com theme)
    
    @staticmethod
    def create_base_embed(title: str, description: str = "", color: int = INFO_COLOR) -> discord.Embed:
        """Create a base embed with consistent styling"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="GeriBot", icon_url="https://cdn.discordapp.com/emojis/♟️.png")
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str = "") -> discord.Embed:
        """Create a success embed (green)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.SUCCESS_COLOR)
    
    @staticmethod
    def create_error_embed(title: str, description: str = "") -> discord.Embed:
        """Create an error embed (red)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.ERROR_COLOR)
    
    @staticmethod
    def create_warning_embed(title: str, description: str = "") -> discord.Embed:
        """Create a warning embed (orange)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.WARNING_COLOR)
    
    @staticmethod
    def create_chess_embed(title: str, description: str = "") -> discord.Embed:
        """Create a chess-themed embed (brown)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.CHESS_COLOR)
    
    @staticmethod
    def create_lichess_embed(title: str, description: str = "") -> discord.Embed:
        """Create a Lichess-themed embed (black)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.LICHESS_COLOR)
    
    @staticmethod
    def create_chess_com_embed(title: str, description: str = "") -> discord.Embed:
        """Create a Chess.com-themed embed (blue)"""
        return EmbedBuilder.create_base_embed(title, description, EmbedBuilder.CHESS_COM_COLOR)
    
    @staticmethod
    def add_field(embed: discord.Embed, name: str, value: str, inline: bool = False) -> discord.Embed:
        """Add a field to an embed"""
        embed.add_field(name=name, value=value, inline=inline)
        return embed
    
    @staticmethod
    def add_thumbnail(embed: discord.Embed, url: str) -> discord.Embed:
        """Add a thumbnail to an embed"""
        embed.set_thumbnail(url=url)
        return embed
    
    @staticmethod
    def add_image(embed: discord.Embed, url: str) -> discord.Embed:
        """Add an image to an embed"""
        embed.set_image(url=url)
        return embed
    
    @staticmethod
    def create_profile_embed(username: str, platform: str, ratings: Dict[str, Any], 
                           profile_url: str, is_online: bool = False) -> discord.Embed:
        """Create a player profile embed"""
        color = EmbedBuilder.LICHESS_COLOR if platform.lower() == "lichess" else EmbedBuilder.CHESS_COM_COLOR
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{platform} Profile: {username}",
            color=color
        )
        
        # Add online status
        status_emoji = "🟢" if is_online else "🔴"
        embed.add_field(name="Status", value=f"{status_emoji} {'Online' if is_online else 'Offline'}", inline=True)
        
        # Add ratings
        for mode, rating in ratings.items():
            if isinstance(rating, (int, float)) and rating > 0:
                embed.add_field(name=mode.title(), value=str(rating), inline=True)
        
        # Add profile link
        embed.add_field(name="Profile", value=f"[View Profile]({profile_url})", inline=False)
        
        return embed
    
    @staticmethod
    def create_game_embed(game_info: Dict[str, Any]) -> discord.Embed:
        """Create a game information embed"""
        embed = EmbedBuilder.create_base_embed(
            title="Chess Game",
            description=f"**{game_info.get('perf', 'Game')}**",
            color=EmbedBuilder.CHESS_COLOR
        )
        
        # Add game details
        if 'opening' in game_info:
            embed.add_field(name="Opening", value=game_info['opening'], inline=False)
        
        if 'result' in game_info:
            embed.add_field(name="Result", value=game_info['result'], inline=True)
        
        if 'link' in game_info:
            embed.add_field(name="Game Link", value=f"[View Game]({game_info['link']})", inline=False)
        
        return embed
    
    @staticmethod
    def create_leaderboard_embed(title: str, players: List[Dict[str, Any]], 
                                platform: str = "Chess") -> discord.Embed:
        """Create a leaderboard embed"""
        color = EmbedBuilder.LICHESS_COLOR if platform.lower() == "lichess" else EmbedBuilder.CHESS_COM_COLOR
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{platform} {title} Leaderboard",
            color=color
        )
        
        # Add leaderboard entries
        leaderboard_text = ""
        for i, player in enumerate(players[:10], 1):  # Top 10
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} **{player['name']}**: {player['rating']}\n"
        
        embed.add_field(name="Rankings", value=leaderboard_text or "No players found", inline=False)
        
        return embed
    
    @staticmethod
    def create_puzzle_embed(puzzle_info: Dict[str, Any]) -> discord.Embed:
        """Create a puzzle embed"""
        embed = EmbedBuilder.create_base_embed(
            title="Chess Puzzle",
            description=f"**Rating:** {puzzle_info.get('rating', 'Unknown')}",
            color=EmbedBuilder.CHESS_COLOR
        )
        
        # Add puzzle details
        if 'clue' in puzzle_info:
            embed.add_field(name="Clue", value=puzzle_info['clue'], inline=False)
        
        if 'themes' in puzzle_info:
            embed.add_field(name="Themes", value=f"||{puzzle_info['themes']}||", inline=True)
        
        if 'solution' in puzzle_info:
            embed.add_field(name="Solution", value=f"||{puzzle_info['solution']}||", inline=True)
        
        if 'toPlay' in puzzle_info:
            embed.add_field(name="To Play", value=puzzle_info['toPlay'], inline=False)
        
        return embed
