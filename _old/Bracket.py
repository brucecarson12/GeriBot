from _old.RRTSchedule import *
from functions import *
import random
import pprint




class Tournament:
    """A Bracket Tournament class for storing referencing and interacting with a double-elimination tournament."""
    def __init__(self,seeds,randseeds=False):
        assert len(seeds) > 1
        random.shuffle(seeds) if randseeds == True else None
        self.seeds = seeds
        self.__wmatches = []
        self.lmatches = []
        self.finals = None
        incoming_seeds = list(map(Player,seeds))
        power_of_two = pow2(len(seeds))
        winner_byes = int(power_of_two - len(seeds))
        incoming_seeds.extend([None]*winner_byes)
        losers  = []
        while len(incoming_seeds) > 1:
            if len(incoming_seeds) == 2:
                self.finals = Match(incoming_seeds[0],incoming_seeds[1])
                print(self.finals)
                break
            else:
                
                continue







def pow2(n:int):
    n = n - 1
    while n & n - 1:
        n = n & n - 1
    return n << 1






def BTourney(seeds: list,randseeds=False):
    seeds.append('BYE') if len(seeds) % 2==1 else None
    random.shuffle(seeds) if randseeds == True else None
    players=[]
    winners=[]
    losers=[]
    WMatches = []
    LMatches  = []
    for seed in seeds:
        players.append(Player(seed))

    for player in players:
        if player.losses == 1:
            losers.append(player)
        elif player.losses == 0:
            winners.append(player)

    for i in range(0,len(winners),2):
        match = Match(players[i].name,players[i+1].name)
        WMatches.append(match)
    
    
    for match in WMatches:
        print(match)



players = ['A','B']

Tournament(players)


