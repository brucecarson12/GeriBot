from csv import reader
import random
import chess
import chess.svg
import cairosvg

def randpuzzle():
    rand = random.randint(2,1405)
    clue = str()
    fentxt = str()
    solutiontxt = str()

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

    board = chess.Board(fentxt)
    boardsvg = chess.svg.board(board=board)
    filename = title + '.png'

    f = open(title + ".SVG", "w")
    f.write(boardsvg)
    f.close()

    cairosvg.svg2png(bytestring=boardsvg, write_to=filename)

    return filename, clue, title, fentxt, 
