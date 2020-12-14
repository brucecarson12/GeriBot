from RRTSchedule import *
import random
import time


PlayerNameList = ['A','B','C','D','E','F']
Players = []
for player in PlayerNameList:
    Players.append(Player(player,None,player))


def MakeRound(Players):
    Losers =[]
    Winners = []
    #Sort players in Losers and Winners Brackets. Doesnt count players who have >1 loss out
    for player in Players:
        if player.losses == 1:
            Losers.append(player)
        elif player.losses == 0:
            Winners.append(player)
            
    if len(Losers) + len(Winners) == 2: #Checks to see if we are on the last match        
        FinalMatch = Match(Losers[0].name,Winners[0].name)
        return FinalMatch , None
    else:
        Losers.append(Player('BYE',None,'BYE')) if len(Losers)%2 ==1 else False
        Winners.append(Player('BYE',None,'BYE')) if len(Winners)%2 ==1 else False #adds BYE player to odd number brackets
        LMatches = []
        WMatches = []
        i=0
        while i <len(Losers):
            LMatches.append(Match(Losers[i].name,Losers[i+1].name))
            i+=2
        i=0
        while i<len(Winners):
            WMatches.append(Match(Winners[i].name,Winners[i+1].name))
            i+=2
        for match in WMatches:
            match.start()
        for match in LMatches:
            match.start()
        return WMatches, LMatches
    

WMatches, LMatches = MakeRound(Players)
print(type(WMatches)is list)
while type(WMatches)is list:
    print("WINNERS:")
    for match in WMatches:
        print(match.vstxt)
        i = 0
        match.addwinner(match.players[i])
        for player in Players:
            if player.name in match.players and player.name != match.winner:
                #print(match.winner,player.name)
                player.losses +=1
                break
    print("LOSERS:")
    for match in LMatches:
        print(match.vstxt)
        i = 0
        match.addwinner(match.players[i])
        for player in Players:
            if player.name in match.players and player.name != match.winner:
                #print(match.winner,player.name)
                player.losses +=1
                break
    WMatches, LMatches = MakeRound(Players)
    time.sleep(2)     

WMatches, LMatches = MakeRound(Players)
print("Final Match:")
print(WMatches.vstxt)