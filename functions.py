from csv import reader
import random
import chess
import chess.svg
import cairo
import cairosvg
import gspread
from RRTSchedule import *
import berserk
import os
import sys


def randpuzzle():
    rand = random.randint(2,1405)
    clue = str()
    fentxt = str()
    solutiontxt = str()
    ori = chess.WHITE

    with open('puzzles.csv', 'r') as puzzles:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(puzzles)
        # Pass reader object to list() to get a list of lists
        puzzlelist = list(csv_reader)[rand]
        #pprint.pprint(list_of_rows)
        clue = str(puzzlelist[0])
        title = str(puzzlelist[1])
        fentxt = str(puzzlelist[2])
        solutiontxt = str(puzzlelist[3])

    if clue.__contains__('Black'):
        ori = chess.BLACK
    board = chess.Board(fentxt)
    boardsvg = chess.svg.board(board=board,orientation=ori)
    filename = title + '.png'

    f = open(title + ".SVG", "w")
    f.write(boardsvg)
    f.close()

    cairosvg.svg2png(bytestring=boardsvg, write_to=filename)

    return filename, clue, title, fentxt, solutiontxt


#----------------------------Double tourney---------------------------------------------------
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
        i,j=0
        while i <len(Losers):
            LMatches.append(Match(Losers[i].name,Losers[i+1].name))
            i+=2
        while j<len(Winners):
            WMatches.append(Match(Winners[j].name,Winners[j+1].name))
            j+=2
        for match in WMatches:
            match.start()
        for match in LMatches:
            match.start()
        return WMatches, LMatches


#---------------------Gsheet functions--------------------------------------------------------
def MakePlayers(PlayerList):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    players =[]
    for p in PlayerList:
        try: 
            cell = sheet.find(p)
            players.append(Player(sheet.row_values(cell.row)[0],sheet.row_values(cell.row)[1],sheet.row_values(cell.row)[2]))
        except:
            current_len = len(sheet.col_values(1))
            new_row = current_len +1
            sheet.update_cell(new_row, 1, p)
            sheet.update_cell(new_row, 3, p)
            sheet.update_cell(new_row, 4, 0)
            sheet.update_cell(new_row, 5, 0)
            sheet.update_cell(new_row, 6, 0)
            sheet.update_cell(new_row, 7, 0)
            players.append(Player( p,None,p))
    return players
  
            


def UpdateSheet(players,tnmtinfo):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    
    for p in players:
        TotalMatches = tnmtinfo.count(p.discord) - tnmtinfo.count(f"{p.discord} vs BYE") - tnmtinfo.count(f"BYE vs {p.discord}") 
        cell = sheet.find(p.discord)
        sheet.update_cell(cell.row,1,p.name)
        sheet.update_cell(cell.row,2,p.li)
        sheet.update_cell(cell.row,5,p.TourneyWins)
        sheet.update_cell(cell.row,7,p.TourneyDraws)
        Losses = TotalMatches - p.TourneyWins - p.TourneyDraws

def UpdateSheetDiscordID(discName,discID=None,lichessname=None):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    try:
        cell = sheet.find(discName)
    except:
        cell = sheet.find(discID)
        sheet.update_cell(cell.row,3,discName)
    if discID:
        sheet.update_cell(cell.row,8,discID)
    if lichessname:
        sheet.update_cell(cell.row,2,lichessname)
    senderman = dict()
    senderman['discName']  =  discName
    senderman['discID'] = discID
    senderman['lichess'] = sheet.cell(cell.row,2).value
    return senderman

def GetStats(discID):
    gc = gspread.service_account(filename='google-credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    try:
        cell = sheet.find(discID)
    except:
        cell = None
        return None
    if cell:
        stats = dict()
        stats['Name']= sheet.cell(cell.row,1).value
        stats['TourneyWins']= sheet.cell(cell.row,4).value
        stats['TotalWins']=sheet.cell(cell.row,5).value
        stats['TotalLoss']=sheet.cell(cell.row,6).value
        stats['TotalDraws']=sheet.cell(cell.row,7).value
        return stats

#--------------------lichess functions w/ test statements-------------------
LiTOKEN = os.getenv('LiToken')
session = berserk.TokenSession(LiTOKEN)
client = berserk.Client(session)

def lichesslink(user1,user2):
    p1 = user1.strip()
    p2 = user2.strip() 
    matchesLi = list(client.games.export_by_player(p1,vs=p2,max=3,ongoing=True))
    recgame = dict()
    recgame['id'] = matchesLi[0]['id']
    recgame['live'] = False
    for match in matchesLi:
        if match['status'] == 'started':
            recgame['id'] = match['id']
            recgame['live'] = True
    recgame['link'] = f"https://lichess.org/{recgame['id']}"
    recgame['giflink'] = f"https://lichess1.org/game/export/gif/{recgame['id']}.gif"
    gameinfo  = client.games.export(recgame['id'])
    recgame['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
    return recgame

def lastgame(user1):
    p1 = user1.strip()
    lastgame  = list(client.games.export_by_player(p1,max=1))
    game = dict()
    game['id'] = lastgame[0]['id']
    game['link'] = f"https://lichess.org/{game['id']}"
    game['gif'] = f"https://lichess1.org/game/export/gif/{game['id']}.gif"
    gameinfo  = client.games.export(lastgame[0]['id'])
    game['opening'] = None
    if 'opening' in gameinfo.keys():
        game['opening'] = f"ECO: {gameinfo['opening']['eco']}, {gameinfo['opening']['name']}"
    return game