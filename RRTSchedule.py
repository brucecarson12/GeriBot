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
            #return_matchs.append(Match(teams[n - 1 - i],teams[i]))
        teams.insert(1, teams.pop())
        fixtures.insert(int(len(fixtures)/2), matchs)
       # fixtures.append(return_matchs)
        matchs = []
        return_matchs = []
    return fixtures

class Player:
    #player in a tournuament
    score = 0

    def __init__(self, name=None, lichess=None, discord = None):
        self.name = name
        self.li = lichess
        self.discord = discord
        self.losses =0
        self.TourneyWins = 0
        self.TourneyDraws = 0
        self.TourneyLoses = 0
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)

    def __repr__(self):
        return f"**{self.name}** {self.score} \n_{self.li}_"  
    
    def __str__(self):
        return f"{self.name}"

    def __lt__(self,other):
        return self.score < other.score

    def add_lichess(self,lichess):
        self.li = lichess
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)
   
    def add_score(self, points):
        self.score += points
        if points == 1:
            self.TourneyWins += 1
        elif points == 0.5:
            self.TourneyDraws += 1
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)


class Match:
    #Match in a tournament
    def __init__(self, wplayer, bplayer, link=None):
        self.wplayer = wplayer
        self.bplayer = bplayer
        self.link = link
        self.vstxt = "{} vs {}".format(wplayer,bplayer)
        self.status = 'pending'     

    def __str__(self):
        return f'{self.wplayer} vs {self.bplayer} \nStatus: {self.status} \nLink: {self.link}'

    def start(self):
        if self.wplayer == "BYE":
            self.winner = self.bplayer
            self.status = 'complete'
        elif self.bplayer == "BYE":
            self.winner = self.wplayer
            self.status = 'complete'
        else:
            self.status = 'started'
        #self.link = findlink(self)

    def round(self,roundno):
        self.roundno = roundno

    def add_link(self,link):
        self.link = link

    def addwinner(self,winner_name):
        if self.status == 'complete':
            return print('Match already scored!')
        else:
            if winner_name == self.wplayer or winner_name == self.bplayer or winner_name == 'Draw':
                self.winner = winner_name
                self.status = 'complete'
                return 
            else:
                return print("They aren't in this match!! Stoopid")