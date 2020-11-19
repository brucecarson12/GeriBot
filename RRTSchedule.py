def rounds(teams):
    if len(teams) % 2==1:
        teams.append('BYE')
    n = len(teams)
    matchs = []
    fixtures = []
    return_matchs = []
    for fixture in range(1, n):
        for i in range(int(n/2)):
            matchs.append("{} VS {}".format(teams[i], teams[n - 1 - i]))
            return_matchs.append("{} VS {}".format( teams[n - 1 - i],teams[i]))
        teams.insert(1, teams.pop())
        fixtures.insert(int(len(fixtures)/2), matchs)
        fixtures.append(return_matchs)
        matchs = []
        return_matchs = []
    return fixtures

class Player:
    #player in a tournuament
    score = 0
    name = str()
    lichess = str()

    def __init__(self, name, lichess=None):
        self.name = name
        self.li = lichess
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)

    def add_lichess(self,lichess):
        self.li = lichess
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)
   
    def add_score(self, points):
        self.score += points
        self.info = "**" + str(self.name) + " " + "**" + str(self.score) + "\n" + str(self.li)


class Match:
    #Match in a tournament
    roundno=1

    def __init__(self, wplayer, bplayer, link=None):
        self.wplayer = wplayer
        self.bplayer = bplayer
        self.link = link

    def __str__(self):
        return super().__str__()