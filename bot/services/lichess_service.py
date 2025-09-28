"""
Lichess API service for GeriBot
"""
import berserk
import requests
from typing import Dict, List, Optional
import os
from bot.config import LICHESS_TOKEN, LICHESS_BASE_URL


class LichessService:
    """Service for interacting with Lichess API"""
    
    def __init__(self):
        self.token = LICHESS_TOKEN
        self.base_url = LICHESS_BASE_URL
        self.session = berserk.TokenSession(self.token)
        self.client = berserk.Client(self.session)
    
    def get_user_ratings(self, username: str) -> Dict:
        """Get user ratings from Lichess"""
        try:
            ratingsget = self.client.users.get_by_id(username)
            stats = {}
            
            if self.client.users.get_public_data(username)['online']:
                stats['txt'] = ":green_circle: Online Now!\n\n"
            else:
                stats['txt'] = ":red_circle: Offline\n\n"
                
            modes = ['bullet', 'blitz', 'rapid', 'classical', 'correspondence']
            emojis = [':gun:', ':cloud_lightning:', ':alarm_clock:', ':clock:', ':sunny:']
            
            for i in modes:
                try:
                    indx = modes.index(i)
                    stats[i] = ratingsget[0]['perfs'][i]['rating']
                    stats['txt'] += f"{emojis[indx]} {stats[i]}  "
                except:
                    continue
                    
            streak_best = ratingsget[0]['perfs']['streak']['score']
            try:
                stats['txt'] += f":jigsaw::cloud_tornado: {streak_best}"
            finally:
                return stats
        except Exception as e:
            raise Exception(f"Failed to get Lichess ratings: {e}")
    
    def get_online_players(self, players: List[str]) -> str:
        """Get list of currently online players"""
        try:
            onlinetxt = f"Currently on Lichess: \n"
            for player in players:
                try:
                    playeron = self.client.users.get_realtime_statuses(player)
                    if playeron[0]['online']:
                        onlinetxt += f" :green_circle: {playeron[0]['name']} \n"
                except:
                    continue
            return onlinetxt
        except Exception as e:
            raise Exception(f"Failed to get online players: {e}")
    
    def get_leaderboard(self, players: List[str], perf: str = 'blitz') -> str:
        """Get leaderboard for a specific performance type"""
        try:
            leaderboardtxt = f"**Lichess {perf.title()} Ratings** \n"
            playerlist = []
            word = 'score' if perf == 'streak' else 'rating'
            
            for player in players:
                try:
                    ratings = self.client.users.get_by_id(player)
                    if ratings[0]['perfs'][perf][word]:
                        rating = ratings[0]['perfs'][perf][word]
                        playerlist.append([player, rating])
                except:
                    continue
            
            def getKey(item):
                return item[1]
                
            leaderboard = sorted(playerlist, key=getKey, reverse=True)
            
            for i in leaderboard:
                leaderboardtxt += f"{i[0]}: {i[1]}\n"
            
            return leaderboardtxt
        except Exception as e:
            raise Exception(f"Failed to get Lichess leaderboard: {e}")
    
    def find_game_between_users(self, user1: str, user2: str) -> Dict:
        """Find the most recent game between two users"""
        try:
            p1 = user1.strip()
            p2 = user2.strip() 
            matchesLi = list(self.client.games.export_by_player(p1, vs=p2, max=3, ongoing=True))
            recgame = {}
            recgame['id'] = matchesLi[0]['id']
            recgame['live'] = False
            
            for match in matchesLi:
                if match['status'] == 'started':
                    recgame['id'] = match['id']
                    recgame['live'] = True
                    
            recgame['link'] = f"https://lichess.org/{recgame['id']}"
            recgame['giflink'] = f"https://lichess1.org/game/export/gif/{recgame['id']}.gif"
            gameinfo = self.client.games.export(recgame['id'])
            recgame['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
            
            return recgame
        except Exception as e:
            raise Exception(f"Failed to find game between users: {e}")
    
    def get_last_game(self, username: str, skip: int = 0) -> Dict:
        """Get the last game played by a user"""
        try:
            p1 = username.strip().lower()
            lastgame = list(self.client.games.export_by_player(p1, max=5))
            game = {}
            game['id'] = lastgame[skip]['id']
            game['end'] = lastgame[skip]['status']
            game['perf'] = f"{lastgame[skip]['variant'].title()} {lastgame[skip]['speed'].title()} Game"
            game['side'] = 'white' if lastgame[skip]['players']['white']['user']['name'].lower() == p1 else 'black'
            game['link'] = f"https://lichess.org/{game['id']}"
            game['gif'] = f"https://lichess1.org/game/export/gif/{game['side']}/{game['id']}.gif"
            gameinfo = self.client.games.export(lastgame[skip]['id'])
            game['analysis'] = None
            game['opening'] = None
            game['badmoves'] = {'inaccuracy': [], 'mistake': [], 'blunder': []}
            
            if 'opening' in gameinfo.keys():
                game['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
            game['status'] = lastgame[skip]['status']
            
            if 'winner' in gameinfo.keys():
                game['winner'] = gameinfo['winner']
            if 'analysis' in gameinfo.keys():
                game['analysis'] = gameinfo['players'][game['side']]['analysis']
                moves = gameinfo['moves'].split(' ')
                startno = 3 if game['side'] == 'black' else 2
                for i in range(startno, len(gameinfo['analysis']), 2):
                    if 'judgment' in gameinfo['analysis'][i]:
                        move = str(f"{str(int((i+2)/2))}. {moves[i]}") if startno == 2 else str(f"{str(int((i+1)/2))}... {moves[i]}")
                        name = gameinfo['analysis'][i]['judgment']['name'].lower()
                        game['badmoves'][name].append(move)
            return game
        except Exception as e:
            raise Exception(f"Failed to get last Lichess game: {e}")
    
    def create_challenge(self, limit: int = 5, increment: int = 0) -> Dict:
        """Create an open challenge on Lichess"""
        try:
            limsec = limit * 60  # convert minutes to seconds
            challenge = self.client.challenges.create_open(clock_limit=limsec, clock_increment=increment)['challenge']
            return challenge
        except Exception as e:
            raise Exception(f"Failed to create Lichess challenge: {e}")
