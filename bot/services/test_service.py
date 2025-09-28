"""
Test service for GeriBot - simplified version without external dependencies
"""
from typing import Dict, List, Optional


class TestService:
    """Test service without external dependencies"""
    
    def __init__(self):
        self.test_data = {
            'lichess': 'testuser',
            'cdc': 'testuser',
            'IRLname': 'Test User'
        }
    
    def get_test_user(self, name: str) -> Dict:
        """Get test user data"""
        return self.test_data
    
    def get_test_ratings(self, username: str) -> Dict:
        """Get test ratings"""
        return {
            'txt': '🔫 Bullet: 1500  ⚡ Blitz: 1600  ⏰ Rapid: 1700  🕐 Classical: 1800'
        }
    
    def get_test_players(self) -> List[str]:
        """Get test player list"""
        return ['testuser1', 'testuser2', 'testuser3']
