from csv import reader
import pprint
import random
import chess
import chess.svg
import cairosvg
import os

def randpuzzle():
    rand = int(random.random()*1405)
    clue = str()
    fentxt = str()
    solutiontxt = str()

    with open('puzzles.csv', 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Pass reader object to list() to get a list of lists
        list_of_rows = list(csv_reader)[rand]
        #pprint.pprint(list_of_rows)
        clue = str(list_of_rows[0])
        title = str(list_of_rows[1])
        fentxt = str(list_of_rows[2])
        solutiontxt = str(list_of_rows[3])

    board = chess.Board(fentxt)
    boardsvg = chess.svg.board(board=board)

    f = open(title + ".SVG", "w")
    f.write(boardsvg)
    f.close()

    cairosvg.svg2png(bytestring=boardsvg, write_to=title + '.png')

    boardpng = open(title + '.png')
    boardpng.close()
    filename = title + '.png'

    return boardpng, filename, clue, title, fentxt, solutiontxt

#boardpng,filename,clue,title,fentxt,solution = randpuzzle()

#print(boardpng,filename,clue,title,fentxt,solution)