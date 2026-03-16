from Utilies.board import Board
from Utilies.piece import Piece
from Utilies.moves import *


def position_key(b: Board):
    fen = b.generate_fen_string().split()
    return " ".join(fen[:4])


def repetition_count(b: Board):
    history = getattr(b, "position_history", None)
    if not history:
        return 1
    return history.count(position_key(b))


def check_terminals(b: Board, color):
    # there are two end of chess games: (Draw or Win)
    # - win only if there checkmate, if white wins
    # the terminal = +1, else the terminal = -1
    #
    # - draw happend when the same move played 3 times,
    # 50-move rule, stalemate, or no enough materials
    result = None
    num_pieces = b.num_pieces

    if repetition_count(b) >= 3:
        result = "Threefold repetition!"
        return 0, result

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


def evaluate(b: Board):
    def _mirror(sq):
        return (7 - (sq // 8)) * 8 + (sq % 8)

    def _pawn_shield_penalty(king_sq, pawn_squares, color):
        if king_sq is None:
            return 0

        rank = king_sq // 8
        file = king_sq % 8
        front_rank = rank + 1 if color == Piece.WHITE else rank - 1
        second_rank = rank + 2 if color == Piece.WHITE else rank - 2

        penalty = 0
        for ff in (file - 1, file, file + 1):
            if not (0 <= ff < 8):
                continue

            found = False
            for rr in (front_rank, second_rank):
                if 0 <= rr < 8 and (rr * 8 + ff) in pawn_squares:
                    found = True
                    break
            if not found:
                penalty += 12
        return penalty

    endgame = (b.num_pieces <= 10)
    score = 0

    white_bishops = 0
    black_bishops = 0

    white_king_sq = None
    black_king_sq = None

    white_pawn_count = [0] * 8
    black_pawn_count = [0] * 8
    max_black_pawn_rank = [-1] * 8
    min_white_pawn_rank = [8] * 8

    white_pawns = set()
    black_pawns = set()
    rooks = []
    pawns = []
    mobility = 0

    for sq in b.active_squares:
        p = b.squares[sq]
        if p == 0:
            continue

        color = p & 24
        pt = p & 7
        base = Piece.get_value(pt)

        if pt == Piece.KING:
            if color == Piece.WHITE:
                white_king_sq = sq
            else:
                black_king_sq = sq
            p_heatmap = Piece.get_heatmap(pt, True) if endgame else Piece.get_heatmap(pt)
            bonus = p_heatmap[sq] if color == Piece.WHITE else p_heatmap[_mirror(sq)]
        else:
            p_heatmap = Piece.get_heatmap(pt)
            bonus = 0
            if p_heatmap is not None:
                bonus = p_heatmap[sq] if color == Piece.WHITE else p_heatmap[_mirror(sq)]

        if pt == Piece.BISHOP:
            if color == Piece.WHITE:
                white_bishops += 1
            else:
                black_bishops += 1

        if pt == Piece.PAWN:
            f = sq % 8
            r = sq // 8
            pawns.append((color, r, f))
            if color == Piece.WHITE:
                white_pawn_count[f] += 1
                white_pawns.add(sq)
                if r < min_white_pawn_rank[f]:
                    min_white_pawn_rank[f] = r
            else:
                black_pawn_count[f] += 1
                black_pawns.add(sq)
                if r > max_black_pawn_rank[f]:
                    max_black_pawn_rank[f] = r

        if pt == Piece.ROOK:
            rooks.append((color, sq))

        if pt in (Piece.KNIGHT, Piece.BISHOP, Piece.ROOK, Piece.QUEEN):
            piece_mobility = len(list(apply_moves(b, sq)))
            if color == Piece.WHITE:
                mobility += piece_mobility
            else:
                mobility -= piece_mobility

        if color == Piece.WHITE:
            score += base + bonus
        else:
            score -= base + bonus

    if white_bishops >= 2:
        score += 30
    if black_bishops >= 2:
        score -= 30

    for color, sq in rooks:
        f = sq % 8
        r = sq // 8
        open_file = (white_pawn_count[f] == 0 and black_pawn_count[f] == 0)
        semi_open = (white_pawn_count[f] == 0) if color == Piece.WHITE else (black_pawn_count[f] == 0)

        bonus = 0
        if open_file:
            bonus += 15
        elif semi_open:
            bonus += 7

        if color == Piece.WHITE and r == 6:
            bonus += 12
        elif color == Piece.BLACK and r == 1:
            bonus += 12

        score += bonus if color == Piece.WHITE else -bonus

    passed_bonus = [0, 5, 10, 20, 35, 60, 90, 0]
    for color, r, f in pawns:
        doubled_penalty = 0
        isolated_penalty = 0

        if color == Piece.WHITE:
            if white_pawn_count[f] > 1:
                doubled_penalty = 12 * (white_pawn_count[f] - 1)

            has_neighbor = False
            for ff in (f - 1, f + 1):
                if 0 <= ff < 8 and white_pawn_count[ff] > 0:
                    has_neighbor = True
                    break
            if not has_neighbor:
                isolated_penalty = 10

            passed = True
            for ff in (f - 1, f, f + 1):
                if 0 <= ff < 8 and max_black_pawn_rank[ff] > r:
                    passed = False
                    break

            score -= doubled_penalty + isolated_penalty
            if passed:
                score += passed_bonus[r]
        else:
            if black_pawn_count[f] > 1:
                doubled_penalty = 12 * (black_pawn_count[f] - 1)

            has_neighbor = False
            for ff in (f - 1, f + 1):
                if 0 <= ff < 8 and black_pawn_count[ff] > 0:
                    has_neighbor = True
                    break
            if not has_neighbor:
                isolated_penalty = 10

            passed = True
            for ff in (f - 1, f, f + 1):
                if 0 <= ff < 8 and min_white_pawn_rank[ff] < r:
                    passed = False
                    break

            score += doubled_penalty + isolated_penalty
            if passed:
                score -= passed_bonus[7 - r]

    if not endgame:
        score -= _pawn_shield_penalty(white_king_sq, white_pawns, Piece.WHITE)
        score += _pawn_shield_penalty(black_king_sq, black_pawns, Piece.BLACK)

    score += 4 * mobility

    if b.side_to_move == Piece.BLACK:
        score = -score

    return score


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
