"""
Puzzle service for GeriBot
"""
import random
import chess
import chess.svg
import cairosvg
import os
from csv import reader
from typing import Tuple, Dict


class PuzzleService:
    """Service for generating chess puzzles"""
    
    def __init__(self):
        self.puzzles_file = 'data/puzzles.csv'
        self.lichess_puzzles_file = 'data/lipuzzlesTEST.csv'
    
    def get_random_puzzle(self) -> Tuple[str, str, str, str, str]:
        """Get a random puzzle from the CSV file"""
        try:
            rand = random.randint(2, 1405)
            clue = str()
            fentxt = str()
            solutiontxt = str()
            ori = chess.WHITE

            with open(self.puzzles_file, 'r') as puzzles:
                csv_reader = reader(puzzles)
                puzzlelist = list(csv_reader)[rand]
                clue = str(puzzlelist[0])
                title = str(puzzlelist[1])
                fentxt = str(puzzlelist[2])
                solutiontxt = str(puzzlelist[3])

            if clue.__contains__('Black'):
                ori = chess.BLACK
            board = chess.Board(fentxt)
            boardsvg = chess.svg.board(board=board, orientation=ori)
            filename = title + '.png'

            cairosvg.svg2png(bytestring=boardsvg, write_to=filename)

            return filename, clue, title, fentxt, solutiontxt
        except Exception as e:
            raise Exception(f"Failed to generate puzzle: {e}")
    
    def get_lichess_puzzle(self) -> Dict:
        """Get a random Lichess puzzle"""
        try:
            rand = random.randint(1, 353269)
            lipuzzle = {}
            ori = chess.WHITE

            with open(self.lichess_puzzles_file, 'r') as puzzles:
                csv_reader = reader(puzzles)
                puzzle = list(csv_reader)[rand]
                lipuzzle['themes'] = str(puzzle[8])
                lipuzzle['gameurl'] = str(puzzle[9])
                lipuzzle['fen'] = str(puzzle[12])
                lipuzzle['toPlay'] = str(puzzle[10])
                lipuzzle['solution'] = str(puzzle[13])
                lipuzzle['ID'] = str(puzzle[0])
                lipuzzle['rating'] = f'{puzzle[4]} +/- {puzzle[5]}'

            if lipuzzle['toPlay'].__contains__('Black'):
                ori = chess.BLACK
            board = chess.Board(lipuzzle['fen'])
            boardsvg = chess.svg.board(board=board, orientation=ori)
            lipuzzle['img'] = f"lipuzzle{lipuzzle['ID']}.png"

            cairosvg.svg2png(bytestring=boardsvg, write_to=lipuzzle['img'])

            return lipuzzle
        except Exception as e:
            raise Exception(f"Failed to generate Lichess puzzle: {e}")
