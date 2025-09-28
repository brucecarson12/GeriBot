"""
Message formatting utilities for GeriBot
"""
from typing import List, Dict, Any, Optional
import discord


class MessageFormatter:
    """Utility class for formatting Discord messages with consistent styling"""
    
    # Emoji constants
    CHESS_PIECES = {
        'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'
    }
    
    STATUS_EMOJIS = {
        'online': '🟢', 'offline': '🔴', 'idle': '🟡', 'dnd': '🔴'
    }
    
    RATING_EMOJIS = {
        'bullet': '🔫', 'blitz': '⚡', 'rapid': '⏰', 'classical': '🕐', 'correspondence': '☀️'
    }
    
    @staticmethod
    def format_rating_display(ratings: Dict[str, int], platform: str = "lichess") -> str:
        """Format ratings for display with emojis"""
        formatted = ""
        for mode, rating in ratings.items():
            if rating and rating > 0:
                emoji = MessageFormatter.RATING_EMOJIS.get(mode, '📊')
                formatted += f"{emoji} **{mode.title()}**: {rating}\n"
        return formatted or "No ratings available"
    
    @staticmethod
    def format_player_status(username: str, is_online: bool, platform: str = "lichess") -> str:
        """Format player online status"""
        status_emoji = MessageFormatter.STATUS_EMOJIS['online'] if is_online else MessageFormatter.STATUS_EMOJIS['offline']
        status_text = "Online" if is_online else "Offline"
        return f"{status_emoji} **{username}** - {status_text} on {platform.title()}"
    
    @staticmethod
    def format_game_info(game_data: Dict[str, Any]) -> str:
        """Format game information for display"""
        lines = []
        
        # Game type and time control
        if 'perf' in game_data:
            lines.append(f"**Game Type:** {game_data['perf']}")
        
        # Players
        if 'vstxt' in game_data:
            lines.append(f"**Players:** {game_data['vstxt']}")
        
        # Opening
        if 'opening' in game_data:
            lines.append(f"**Opening:** {game_data['opening']}")
        
        # Result
        if 'result' in game_data:
            lines.append(f"**Result:** {game_data['result']}")
        
        # Analysis
        if 'analysis' in game_data and game_data['analysis']:
            analysis = game_data['analysis']
            lines.append(f"**Average Centipawn Loss:** {analysis.get('acpl', 'N/A')}")
            
            # Mistakes breakdown
            if 'badmoves' in game_data:
                badmoves = game_data['badmoves']
                for mistake_type, moves in badmoves.items():
                    if moves:
                        count = len(moves)
                        moves_str = ', '.join(moves[:3])  # Show first 3 moves
                        if len(moves) > 3:
                            moves_str += f" (+{len(moves)-3} more)"
                        lines.append(f"**{mistake_type.title()}** ({count}): {moves_str}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_leaderboard(players: List[Dict[str, Any]], title: str = "Leaderboard") -> str:
        """Format leaderboard for display"""
        if not players:
            return f"**{title}**\nNo players found"
        
        lines = [f"**{title}**"]
        for i, player in enumerate(players[:10], 1):  # Top 10
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            lines.append(f"{medal} **{player['name']}**: {player['rating']}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_performance_rating(score: int, opponent_ratings: List[int], 
                                 perf_rating: int, norm_info: str = "") -> str:
        """Format performance rating calculation results"""
        avg_rating = sum(opponent_ratings) / len(opponent_ratings) if opponent_ratings else 0
        
        lines = [
            f"**Performance Rating Calculation**",
            f"📊 **Your Score:** {score}/{len(opponent_ratings)}",
            f"📈 **Average Opponent Rating:** {int(avg_rating)}",
            f"🎯 **Performance Rating:** {perf_rating}",
        ]
        
        if norm_info:
            lines.append(f"🏆 **{norm_info}**")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_puzzle_info(puzzle_data: Dict[str, Any]) -> str:
        """Format puzzle information for display"""
        lines = []
        
        if 'clue' in puzzle_data:
            lines.append(f"**Clue:** {puzzle_data['clue']}")
        
        if 'title' in puzzle_data:
            lines.append(f"**Game:** {puzzle_data['title']}")
        
        if 'rating' in puzzle_data:
            lines.append(f"**Rating:** {puzzle_data['rating']}")
        
        if 'themes' in puzzle_data:
            lines.append(f"**Themes:** ||{puzzle_data['themes']}||")
        
        if 'solution' in puzzle_data:
            lines.append(f"**Solution:** ||{puzzle_data['solution']}||")
        
        if 'toPlay' in puzzle_data:
            lines.append(f"**To Play:** {puzzle_data['toPlay']}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_error_message(error_type: str, details: str = "") -> str:
        """Format error messages consistently"""
        error_messages = {
            'not_found': f"❌ **User Not Found**\n{details}",
            'api_error': f"⚠️ **API Error**\n{details}",
            'file_error': f"📁 **File Error**\n{details}",
            'validation_error': f"✏️ **Input Error**\n{details}",
            'permission_error': f"🔒 **Permission Denied**\n{details}",
            'rate_limit': f"⏱️ **Rate Limited**\n{details}",
            'general': f"❌ **Error**\n{details}"
        }
        
        return error_messages.get(error_type, error_messages['general'])
    
    @staticmethod
    def format_success_message(message: str, details: str = "") -> str:
        """Format success messages consistently"""
        return f"✅ **{message}**\n{details}" if details else f"✅ **{message}**"
    
    @staticmethod
    def format_help_message(command_name: str, description: str, 
                           usage: str = "", examples: List[str] = None) -> str:
        """Format help messages for commands"""
        lines = [f"**{command_name}** - {description}"]
        
        if usage:
            lines.append(f"**Usage:** `{usage}`")
        
        if examples:
            lines.append("**Examples:**")
            for example in examples:
                lines.append(f"• `{example}`")
        
        return '\n'.join(lines)
