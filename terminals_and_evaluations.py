from board import Board
from piece import Piece
from moves import has_legal_move, is_king_in_check

def check_terminals(b: Board, color):
    # there are two end of chess games: (Draw or Win)
    # - win only if there checkmate, if white wins
    #   the terminal = +1, else the terminal = -1
    #
    # - draw happend when the same move played 3 times,
    #   50-move rule, stalemate, or no enough materials

    result = None
    Draw = 0
    num_pieces = b.num_pieces

    if num_pieces <= 3:
        minor = True
        for sq in b.active_squares:
            pt = b.squares[sq] & 7
            if pt == Piece.BISHOP or pt == Piece.KNIGHT:
                minor = True
            elif pt != Piece.KING:
                minor = False
                break
        if minor:
            result = "No enough materials!"
            return Draw, result
    
    if b.halfmove_clock >= 50:
        result = "50-move rule!"
        return Draw, result
    
    if not has_legal_move(b):
        if is_king_in_check(b, b.side_to_move):
            if color == Piece.WHITE:
                result = "White wins!"
                return 1, result
            else:
                result = "Black wins!"
                return -1, result
        else:
            result = "This is Stalemate!"
            return Draw, result
        
    return None, result

def get_evaluation(b: Board):
    pass