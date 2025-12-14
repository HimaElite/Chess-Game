from board import Board
from piece import Piece
from game import *
from moves import *

def check_terminals(b: Board, color):
    # there are two end of chess games: (Draw or Win)
    # - win only if there checkmate, if white wins
    #   the terminal = +1, else the terminal = -1
    #
    # - draw happend when the same move played 3 times,
    #   50-move rule, stalemate, or no enough materials
    result = None
    Draw = 0
    num_pieces = 0
    for sq in b.squares:
        if sq != 0:
            num_pieces += 1

    if num_pieces == 2:
        result = "No enough materials!"
        return Draw, result
    
    if b.halfmove_clock == 50:
        result = "50-move rule!"
        return Draw, result
    
    if not all_legal_moves(b):
        if is_in_check(b, b.side_to_move):
            if color == Piece.WHITE:
                result = "White wins!"
                return 1, result
            else:
                result = "Black wins!"
                return -1, result
        else:
            result = "This is Stalemate!"
            return Draw, result
        
    return False, result

def get_evaluation(b: Board):
    pass