from csv import reader
import random
import chess
import chess.svg
import cairo
import cairosvg
import gspread
from RRTSchedule import *


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
    gc = gspread.service_account(filename='credentials.json')
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
            sheet.update_cell(new_row, 3, p)
            sheet.update_cell(new_row, 4, 0)
            sheet.update_cell(new_row, 5, 0)
            sheet.update_cell(new_row, 6, 0)
            sheet.update_cell(new_row, 7, 0)
            players.append(Player( None,None,p))
    return players
            



def UpdateSheet(players,tnmtinfo):
    gc = gspread.service_account(filename='credentials.json')
    Book = gc.open('Chess_Tourney')
    sheet = Book.get_worksheet(0)
    
    for p in players:
        TotalMatches = tnmtinfo.count(p.name) - tnmtinfo.count(f"{p.discord} vs BYE") - tnmtinfo.count(f"BYE vs {p.discord}") 
        cell = sheet.find(p.discord)
        sheet.update_cell(cell.row,1,p.name)
        sheet.update_cell(cell.row,2,p.li)
        sheet.update_cell(cell.row,5,p.TourneyWins)
        sheet.update_cell(cell.row,7,p.TourneyDraws)
        Losses = TotalMatches - p.TourneyWins - p.TourneyDraws

