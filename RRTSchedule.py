def rounds(teams):
    if len(teams) % 2==1:
        teams.append('BYE')
    n = len(teams)
    matchs = []
    fixtures = []
    return_matchs = []
    for fixture in range(1, n):
        for i in range(int(n/2)):
            matchs.append(Match(teams[i], teams[n - 1 - i]))
            return_matchs.append(Match(teams[n - 1 - i],teams[i]))
        teams.insert(1, teams.pop())
        fixtures.insert(int(len(fixtures)/2), matchs)
        fixtures.append(return_matchs)
        matchs = []
        return_matchs = []
    return fixtures

class Player:
    #player in a tournuament
    score = 0

    def __init__(self, name, lichess=None):
        self.name = name
        self.li = lichess
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)

    def __repr__(self):
        return f"**{self.name}** {self.score} \n_{self.li}_"  
    
    def __str__(self):
        return f"Name: **{self.name}** Score: {self.score} \n usrnamelichess:_{self.li}_"

    def add_lichess(self,lichess):
        self.li = lichess
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)
   
    def add_score(self, points):
        self.score += points
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)


class Match:
    #Match in a tournament
    def __init__(self, wplayer, bplayer, link=None):
        self.wplayer = wplayer
        self.bplayer = bplayer
        self.link = link
        self.vstxt = "{} vs {}".format(wplayer,bplayer)
        self.status = 'ongoing'

    def __str__(self):
        return f'{self.wplayer} vs {self.bplayer} \nStatus: {self.status} \nLink: {self.link}'

    def start(self):
        self.status = 'started'
        #self.link = findlink(self)

    def round(self,roundno):
        self.roundno = roundno

    def add_link(self,link):
        self.link = link

    def winner(self,winner_name):
        if winner_name == self.wplayer or winner_name == self.bplayer or winner_name == 'Draw':
            self.winner = winner_name
            self.status = 'complete'
            return 
        else:
            return print("They aren't in this match!! Stoopid")
