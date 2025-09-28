"""
Database service for GeriBot using Google Sheets
"""
import gspread
from typing import Dict, List, Optional
from bot.config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_NAME


class DatabaseService:
    """Service for database operations using Google Sheets"""
    
    def __init__(self):
        self.gc = gspread.service_account(filename=GOOGLE_CREDENTIALS_FILE)
        self.book = self.gc.open(GOOGLE_SHEET_NAME)
        self.sheet = self.book.get_worksheet(0)
    
    def update_discord_user(self, disc_name: str, disc_id: Optional[int] = None, 
                          irl_name: Optional[str] = None, lichess_name: Optional[str] = None, 
                          cdc_name: Optional[str] = None) -> Dict:
        """Update or create a Discord user in the database"""
        try:
            if disc_id:
                cell = self.sheet.find(str(disc_id))
                if irl_name:
                    self.sheet.update_cell(cell.row, 1, irl_name)
                if lichess_name:
                    self.sheet.update_cell(cell.row, 2, lichess_name)
                if cdc_name:
                    self.sheet.update_cell(cell.row, 9, cdc_name)
            else:
                self.sheet.append_row([irl_name, lichess_name, disc_name, 0, 0, 0, 0, str(disc_id), str(cdc_name)])
                cell = self.sheet.find(str(disc_id))
            
            user_info = {
                'discName': disc_name,
                'discID': disc_id,
                'lichess': self.sheet.cell(cell.row, 2).value,
                'cdc': self.sheet.cell(cell.row, 9).value,
                'IRLname': self.sheet.cell(cell.row, 1).value
            }
            return user_info
        except Exception as e:
            raise Exception(f"Failed to update Discord user: {e}")
    
    def add_lichess_user(self, lichess_name: str, disc_name: str, disc_id: int, 
                        irl_name: Optional[str] = None) -> Dict:
        """Add a Lichess user to the database"""
        try:
            try:
                cell = self.sheet.find(str(disc_id))
                self.sheet.update_cell(cell.row, 2, lichess_name)
                if irl_name:
                    self.sheet.update_cell(cell.row, 1, irl_name)
                else:
                    self.sheet.update_cell(cell.row, 1, disc_name)
            except:
                self.sheet.append_row([irl_name, lichess_name, disc_name, 0, 0, 0, 0, str(disc_id)])
            
            cell = self.sheet.find(lichess_name)
            user_info = {
                'discName': self.sheet.cell(cell.row, 3).value,
                'discID': disc_id,
                'lichess': self.sheet.cell(cell.row, 2).value,
                'IRLname': self.sheet.cell(cell.row, 1).value
            }
            return user_info
        except Exception as e:
            raise Exception(f"Failed to add Lichess user: {e}")
    
    def get_user_stats(self, disc_id: int) -> Dict:
        """Get user statistics from the database"""
        try:
            cell = self.sheet.find(str(disc_id))
            stats = {
                'Name': self.sheet.cell(cell.row, 1).value,
                'TourneyWins': self.sheet.cell(cell.row, 4).value,
                'TotalWins': self.sheet.cell(cell.row, 5).value,
                'TotalLoss': self.sheet.cell(cell.row, 6).value,
                'TotalDraws': self.sheet.cell(cell.row, 7).value
            }
            return stats
        except Exception as e:
            raise Exception(f"Failed to get user stats: {e}")
    
    def get_lichess_players(self) -> List[str]:
        """Get list of Lichess players from the database"""
        try:
            cell = self.sheet.find('Lichess Username')
            players = self.sheet.col_values(cell.col)[1:]
            return [x for x in players if str(x) != '']
        except Exception as e:
            raise Exception(f"Failed to get Lichess players: {e}")
    
    def get_chess_com_players(self) -> List[str]:
        """Get list of Chess.com players from the database"""
        try:
            cell = self.sheet.find('ChessCom Username')
            players = self.sheet.col_values(cell.col)[1:]
            return [x for x in players if str(x) != '']
        except Exception as e:
            raise Exception(f"Failed to get Chess.com players: {e}")
