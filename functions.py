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
    return recgame


#game = lichesslink('Bnyce','m_0887')
#print(game['link'])
#print(f"https://lichess1.org/game/export/gif/{game['id']}.gif", game['live'])
