from functions import *

"""
A match represents a single match in a tournament, between 2 participants.
It adds empty participants as placeholders for the winner and loser,
so they can be accessed as individual object pointers.
"""
from participant import Participant

class Match:
    """
    A match represents a single match in a tournament, between 2 participants.
    It adds empty participants as placeholders for the winner and loser,
    so they can be accessed as individual object pointers.
    """
    def __init__(self, white, black):
        self.__white = white
        self.__black = black
        self.__winner = Participant()
        self.__loser = Participant()
        self.link  = None
        self.status = 'pending'

    def set_winner(self, competitor):
        """
        When the match is over, set the winner competitor here and the loser will be set too.
        """
        if competitor == self.__white.get_competitor():
            self.__winner.set_competitor(competitor)
            self.__loser.set_competitor(self.__black.get_competitor())
            self.status  = '1-0'
        elif competitor == self.__black.get_competitor():
            self.__winner.set_competitor(competitor)
            self.__loser.set_competitor(self.__white.get_competitor())
            self.status  = '0-1'
        else:
            raise Exception("Invalid competitor")
        if self.__white.li and self.__black.li and not self.link:
            recgame = lichesslink(self.__white.li,self.__black.li)
            self.link = recgame['link']

    def get_winner_participant(self):
        """
        If the winner is set, get it here. Otherwise this return None.
        """
        return self.__winner

    def get_loser_participant(self):
        """
        If the winner is set, you can get the loser here. Otherwise this return None.
        """
        return self.__loser

    def get_participants(self):
        """
        Get the left and right participants in a list.
        """
        return [self.__white, self.__black]
    
    def start_match(self):
        self.status = 'started'

    def is_ready_to_start(self):
        """
        This returns True if both of the participants coming in have their competitors "resolved".
        This means that the match that the participant is coming from is finished.
        It also ensure that the winner hasn't been set yet.
        """
        is_left_resolved = self.__white.get_competitor() is not None
        is_right_resolved = self.__black.get_competitor() is not None
        is_winner_resolved = self.__winner.get_competitor() is not None
        return is_left_resolved and is_right_resolved and not is_winner_resolved
