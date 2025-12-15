from board import Board
from piece import Piece
from moves import *

def check_terminals(b: Board, color):
    # there are two end of chess games: (Draw or Win)
    # - win only if there checkmate, if white wins
    #   the terminal = +1, else the terminal = -1
    #
    # - draw happend when the same move played 3 times,
    #   50-move rule, stalemate, or no enough materials

    result = None
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
            return 0, result
    
    if b.halfmove_clock >= 50:
        result = "50-move rule!"
        return 0, result
    
    if not all_legal_moves(b):
        if is_king_in_check(b, b.side_to_move):
            if color == Piece.WHITE:
                result = "White wins!"
                return 1, result
            else:
                result = "Black wins!"
                return -1, result
        else:
            result = "This is Stalemate!"
            return 0, result
        
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

def evaluate(b: Board):
    white_eval, black_eval = count_materials_value(b)

    evaluation = white_eval - black_eval
    if b.side_to_move == Piece.WHITE:
        return evaluation
    else:
        return -evaluation

def count_materials_value(b: Board):
    white_materials = 0
    black_materials = 0
    for i in b.active_squares:
        sq = b.squares[i]
        pt = sq & 7
        color = sq & 24
        if color == Piece.WHITE:
            white_materials += Piece.get_value(pt)
        else:
            black_materials += Piece.get_value(pt)

    return white_materials, black_materials
