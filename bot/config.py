"""
Configuration settings for GeriBot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Configuration
DISCORD_TOKEN = os.getenv("DiscToken")
BOT_PREFIX = '$'
BOT_INTENTS = ['message_content', 'guilds', 'members']

# API Tokens
LICHESS_TOKEN = os.getenv('LiToken')

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE = 'google-credentials.json'
GOOGLE_SHEET_NAME = 'Chess_Tourney'

# File Paths
DATA_DIR = 'data'
TEMP_DIR = 'temp'

# Chess.com API Configuration
CHESS_COM_BASE_URL = 'https://api.chess.com'

# Lichess API Configuration
LICHESS_BASE_URL = 'https://lichess.org/api'

# Tournament Configuration
DEFAULT_TIME_LIMIT = 5  # minutes
DEFAULT_INCREMENT = 0    # seconds

# Performance Rating Configuration
PERFORMANCE_RATING_BASE = 800
