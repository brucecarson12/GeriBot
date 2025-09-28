"""
The Participant class represents a participant in a specific match.
It can be used as a placeholder until the participant is decided.
"""
from typing import Optional


class Participant:
    """
    The Participant class represents a participant in a specific match.
    It can be used as a placeholder until the participant is decided.
    """
    
    def __init__(self, competitor: Optional[str] = None, discord: Optional[str] = None, lichess: Optional[str] = None):
        self.competitor = competitor
        self.li = lichess
        self.discord = discord
        self.score = 0
        self.TourneyWins = 0
        self.TourneyDraws = 0
        self.TourneyLoses = 0

    def __repr__(self) -> str:
        return f"**{self.competitor}** {self.score} \n_{self.li}_"  

    def __str__(self) -> str:
        return f"{self.competitor}"
        
    def __lt__(self, other) -> bool:
        return self.score < other.score

    def get_competitor(self) -> Optional[str]:
        """
        Return the competitor that was set,
        or None if it hasn't been decided yet
        """
        return self.competitor

    def set_competitor(self, competitor: str) -> None:
        """
        Set competitor after you've decided who it will be,
        after a previous match is completed.
        """
        self.competitor = competitor

    def updateli(self, li: str) -> None:
        """Update the Lichess username"""
        self.li = li

    def add_score(self, points: float) -> None:
        """Add points to the participant's score"""
        self.score += points
        if points == 1:
            self.TourneyWins += 1
        elif points == 0.5:
            self.TourneyDraws += 1
