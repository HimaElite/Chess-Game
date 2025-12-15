from board import Board
from piece import Piece
from moves import *

def has_legal_move(b):
    # this is for checkmate condition
    color = b.side_to_move
    active = list(b.active_squares)
    for i in active:
        sq = b.squares[i]
        if (sq & 24) != color:
            continue
        for from_sq, to_sq, promo in apply_moves(b, i):
            undo = make_move(b, from_sq, to_sq, promo, update_fen=False)
            illegal = is_king_in_check(b, color)
            undo_move(b, undo, update_fen=False)
            if not illegal:
                return True
    return False

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
    def _mirror(sq):
        return (7 - (sq // 8)) * 8 + (sq % 8)

    endgame = (b.num_pieces <= 10)
    score = 0
    for sq in b.active_squares:
        p = b.squares[sq]
        if p == 0:
            continue

        color = p & 24
        pt = p & 7
        base = Piece.get_value(pt)

        if pt == Piece.KING:
            p_heatmap = Piece.get_heatmap(pt, True) if endgame else Piece.get_heatmap(pt)
            bonus = p_heatmap[sq] if color == Piece.WHITE else p_heatmap[_mirror(sq)]
        else:
            p_heatmap = Piece.get_heatmap(pt)
            bonus = p_heatmap[sq] if (p_heatmap is not None and color == Piece.WHITE) else 0
            if p_heatmap is not None and color == Piece.BLACK:
                bonus = p_heatmap[_mirror(sq)]

        if color == Piece.WHITE:
            score += base + bonus
        else:
            score -= base + bonus

    if b.side_to_move == Piece.BLACK:
        score = -score

    return score
