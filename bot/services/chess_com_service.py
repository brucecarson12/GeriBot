"""
Chess.com API service for GeriBot
"""
import chessdotcom as cdc
from typing import Dict, List, Optional
import re
import io
import chess.pgn
import pgn2gif
import datetime as dt
from bot.config import CHESS_COM_BASE_URL


class ChessComService:
    """Service for interacting with Chess.com API"""
    
    def __init__(self):
        self.base_url = CHESS_COM_BASE_URL
    
    def get_player_stats(self, username: str) -> Dict:
        """Get player statistics from Chess.com"""
        try:
            ratings = cdc.get_player_stats(username)
            stats = {}
            modes = ['bullet', 'blitz', 'rapid', 'classical', 'correspondence']
            emojis = [':gun:', ':cloud_lightning:', ':alarm_clock:', ':clock:', ':sunny:']
            
            try:
                if cdc.is_player_online(username).json['online']:
                    stats['txt'] = ":green_circle: Online Now!\n\n"
                else:
                    stats['txt'] = ":red_circle: Offline\n\n"
            except:
                stats['txt'] = "\n"
                
            for i in modes:
                try:
                    indx = modes.index(i)
                    search = "chess_" + i
                    stats[i] = ratings.json['stats'][search]['last']['rating']
                    stats['txt'] += f"{emojis[indx]} {stats[i]}  "
                except:
                    continue
                    
            try:
                rush_best = ratings.json['stats']['puzzle_rush']['best']['score']
                stats['txt'] += f":jigsaw::cloud_tornado: {rush_best}"
            finally:
                return stats
        except Exception as e:
            raise Exception(f"Failed to get Chess.com stats: {e}")
    
    def get_last_game(self, username: str) -> Dict:
        """Get the last game played by a user"""
        try:
            today = dt.datetime.today()
            game = cdc.get_player_games_by_month(username, year=today.year, month=today.month)
            
            if not game.json['games']:
                game = cdc.get_player_games_by_month(username, year=today.year, month=today.month-1)
            
            nogames = len(game.json['games']) - 1
            lastgame = game.json['games'][nogames]
            
            lastgamedict = {
                'pgn': lastgame['pgn'],
                'url': lastgame['url'],
                'wplayer': {
                    'name': lastgame['white']['username'],
                    'rating': lastgame['white']['rating']
                },
                'bplayer': {
                    'name': lastgame['black']['username'],
                    'rating': lastgame['black']['rating']
                },
                'vstxt': f"{lastgame['white']['username']} _{lastgame['white']['rating']}_ vs. {lastgame['black']['username']} _{lastgame['black']['rating']}_",
                'result': f"{lastgame['pgn'][-6]}"
            }

            lastgamedict['pgn4gif'] = re.sub(r'{\[%clk \d+:\d+:\d+(\.\d+)?\]} ', '', lastgame['pgn'])
            lastgamedict['pgn4gif'] = re.sub(r' [0-9]\.\.\.|[1-9][0-9]\.\.\. ', '', lastgamedict['pgn4gif'])
                
            # Create gif
            pgn = io.StringIO(lastgamedict['pgn4gif'])
            gamepy = chess.pgn.read_game(pgn)
            print(gamepy, file=open("temp/temp.pgn", "w"))
            lastgamedict['result'] = gamepy.headers['Result']
            reverse = 0
            if lastgamedict['bplayer']['name'] == username:
                reverse = 1
            creator = pgn2gif.PgnToGifCreator(reverse=reverse, duration=0.5, ws_color='#ebecd0', bs_color='#779556')
            creator.create_gif("temp/temp.pgn", out_path="temp/chess.gif")
            
            return lastgamedict
        except Exception as e:
            raise Exception(f"Failed to get last Chess.com game: {e}")
    
    def get_leaderboard(self, perf: str = 'blitz') -> str:
        """Get leaderboard for a specific performance type"""
        # This would need to be implemented with database integration
        # For now, return a placeholder
        return f"Chess.com {perf.title()} leaderboard functionality needs database integration"
