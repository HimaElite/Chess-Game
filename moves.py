from piece import Piece
from board import *


# ------------------- HELPERS ------------------- #

def _rank(index):
    return index // 8

def _file(index):
    return index % 8

def _in_board(index):
    return 0 <= index <= 63

def _opponent(color):
    return Piece.BLACK if color == Piece.WHITE else Piece.WHITE

# =============================================== #



# ------------------- GENERATE MOVES ------------------- #

def _sliding_moves(b, index, color, directions):
    moves = []
    for y, x in directions:
        r, f = _rank(index) + y, _file(index) + x
        while 0 <= r < 8 and 0 <= f < 8:
            sq = r * 8 + f
            target = b.squares[sq]
            if target == 0:
                moves.append((index, sq, None))
            else:
                if (target & 24) != color:
                    moves.append((index, sq, None))
                break
            r += y
            f += x
    return moves

def _pawn_moves(b, index, color):
    moves = []
    r, f = _rank(index), _file(index)
    forward = 8 if color == Piece.WHITE else -8
    start_rank = 1 if color == Piece.WHITE else 6
    promo_rank = 7 if color == Piece.WHITE else 0

    one = index + forward
    if _in_board(one) and b.squares[one] == 0:
        if _rank(one) == promo_rank:
            for promo in [Piece.QUEEN, Piece.ROOK, Piece.BISHOP, Piece.KNIGHT]:
                moves.append((index, one, promo))
        else:
            moves.append((index, one, None))

        two = index + 2 * forward
        if r == start_rank and b.squares[two] == 0:
            moves.append((index, two, None))

    if color == Piece.WHITE:
        caps = [7, 9]
    else:
        caps = [-7, -9]

    for off in caps:
        to_sq = index + off
        if not _in_board(to_sq):
            continue
        if abs(_file(to_sq) - f) != 1:
            continue

        target = b.squares[to_sq]
        if target != 0 and (target & 24) != color:
            if _rank(to_sq) == promo_rank:
                for promo in [Piece.QUEEN, Piece.ROOK, Piece.BISHOP, Piece.KNIGHT]:
                    moves.append((index, to_sq, promo))
            else:
                moves.append((index, to_sq, None))

        if b.en_passant is not None and b.en_passant == to_sq:
            moves.append((index, to_sq, None))

    return moves

def _knight_moves(b, index, color):
    moves = []
    r, f = _rank(index), _file(index)
    offsets = [17, 15, 10, 6, -6, -10, -15, -17]
    for off in offsets:
        to_sq = index + off
        if not _in_board(to_sq):
            continue
        tr, tf = _rank(to_sq), _file(to_sq)
        if not ((abs(r - tr) == 2 and abs(f - tf) == 1) or (abs(r - tr) == 1 and abs(f - tf) == 2)):
            continue
        target = b.squares[to_sq]
        if target == 0 or (target & 24) != color:
            moves.append((index, to_sq, None))
    return moves

def _king_moves(b, index, color):
    moves = []
    r, f = _rank(index), _file(index)
    offsets = [9, 8, 7, 1, -1, -7, -8, -9]
    for off in offsets:
        to_sq = index + off
        if not _in_board(to_sq):
            continue
        if abs(_file(to_sq) - f) > 1:
            continue
        target = b.squares[to_sq]
        if target == 0 or (target & 24) != color:
            moves.append((index, to_sq, None))

    if color == Piece.WHITE and index == 4:
        if 'K' in b.castling:
            if b.squares[5] == 0 and b.squares[6] == 0 and b.squares[7] == (Piece.WHITE | Piece.ROOK):
                if not is_king_in_check(b, Piece.WHITE) and not is_square_attacked(b, 5, Piece.BLACK) and not is_square_attacked(b, 6, Piece.BLACK):
                    moves.append((4, 6, None))
        if 'Q' in b.castling:
            if b.squares[1] == 0 and b.squares[2] == 0 and b.squares[3] == 0 and b.squares[0] == (Piece.WHITE | Piece.ROOK):
                if not is_king_in_check(b, Piece.WHITE) and not is_square_attacked(b, 3, Piece.BLACK) and not is_square_attacked(b, 2, Piece.BLACK):
                    moves.append((4, 2, None))

    if color == Piece.BLACK and index == 60:
        if 'k' in b.castling:
            if b.squares[61] == 0 and b.squares[62] == 0 and b.squares[63] == (Piece.BLACK | Piece.ROOK):
                if not is_king_in_check(b, Piece.BLACK) and not is_square_attacked(b, 61, Piece.WHITE) and not is_square_attacked(b, 62, Piece.WHITE):
                    moves.append((60, 62, None))
        if 'q' in b.castling:
            if b.squares[57] == 0 and b.squares[58] == 0 and b.squares[59] == 0 and b.squares[56] == (Piece.BLACK | Piece.ROOK):
                if not is_king_in_check(b, Piece.BLACK) and not is_square_attacked(b, 59, Piece.WHITE) and not is_square_attacked(b, 58, Piece.WHITE):
                    moves.append((60, 58, None))

    return moves

def apply_moves(b, index):
    sq = b.squares[index]
    if sq == 0:
        return []

    pt = sq & 7
    color = sq & 24

    if pt == Piece.PAWN:
        return _pawn_moves(b, index, color)
    if pt == Piece.KNIGHT:
        return _knight_moves(b, index, color)
    if pt == Piece.BISHOP:
        return _sliding_moves(b, index, color, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
    if pt == Piece.ROOK:
        return _sliding_moves(b, index, color, [(1, 0), (-1, 0), (0, 1), (0, -1)])
    if pt == Piece.QUEEN:
        return _sliding_moves(b, index, color, [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)])
    if pt == Piece.KING:
        return _king_moves(b, index, color)

    return []

def _update_castling_rights(b, from_sq, to_sq, moved_piece, captured_piece):
    if (moved_piece & 7) == Piece.KING:
        if (moved_piece & 24) == Piece.WHITE:
            b.castling = b.castling.replace('K', '').replace('Q', '')
        else:
            b.castling = b.castling.replace('k', '').replace('q', '')

    if ((moved_piece & 7) == Piece.ROOK) or (captured_piece != 0 and (captured_piece & 7) == Piece.ROOK):
        if from_sq == 0:
            b.castling = b.castling.replace('Q', '')
        elif from_sq == 7:
            b.castling = b.castling.replace('K', '')
        elif from_sq == 56:
            b.castling = b.castling.replace('q', '')
        elif from_sq == 63:
            b.castling = b.castling.replace('k', '')


# ====================================================== #



# ------------------- MOVE ACTION ------------------- #

def move_generation_test(b, depth):
    if depth <= 0:
        return 1
    
    color = b.side_to_move
    num_positions = 0
    active = list(b.active_squares)
    for i in active:
        sq = b.squares[i]
        if sq == 0:
            continue
        if (sq & 24) != color:
            continue

        for from_sq, to_sq, promo in apply_moves(b, i):
            undo = make_move(b, from_sq, to_sq, promo, update_fen=False)
            if not is_king_in_check(b, color):
                if depth == 1:
                    num_positions += 1
                else:
                    num_positions += move_generation_test(b, depth - 1)
            undo_move(b, undo, update_fen=False)

    return num_positions

def take_move(b, from_pos, to_pos, promotion=None):
    # check the action that player want to do

    try:
        from_sq = b.get_index(from_pos)
        to_sq = b.get_index(to_pos)
    except Exception:
        print("Invalid square format!")
        return False

    sq = b.squares[from_sq]
    if sq == 0:
        print("No piece at source square!")
        return False

    if (sq & 24) != b.side_to_move:
        print("This is the oppenet's square!")
        return False

    legals = legal_moves(b, from_sq)
    if to_sq not in legals:
        print("Illegal move!")
        return False

    promo_piece = None
    if promotion is not None:
        p = str(promotion).lower().strip()
        if p == 'q':
            promo_piece = Piece.QUEEN
        elif p == 'r':
            promo_piece = Piece.ROOK
        elif p == 'b':
            promo_piece = Piece.BISHOP
        elif p == 'n':
            promo_piece = Piece.KNIGHT

    undo = make_move(b, from_sq, to_sq, promo_piece)
    return undo

def make_move(b, from_sq, to_sq, promotion=None, update_fen=True):
    moved_piece = b.squares[from_sq]
    captured_piece = b.squares[to_sq]

    undo = {
        'from': from_sq,
        'to': to_sq,
        'moved': moved_piece,
        'captured': captured_piece,
        'prev_side': b.side_to_move,
        'prev_castling': b.castling,
        'prev_ep': b.en_passant,
        'prev_halfmove': b.halfmove_clock,
        'prev_fullmove': b.fullmove_number,
        'prev_num_pieces': b.num_pieces,
        'prev_white_king': b.white_king,
        'prev_black_king': b.black_king,
        'ep_capture_sq': None,
        'castle_rook_from': None,
        'castle_rook_to': None,
        'castle_rook_piece': 0
    }

    b.en_passant = None
    color = moved_piece & 24
    pt = moved_piece & 7

    if pt == Piece.PAWN or captured_piece != 0:
        b.halfmove_clock = 0
    else:
        b.halfmove_clock += 1

    if pt == Piece.PAWN and undo['prev_ep'] is not None and to_sq == undo['prev_ep'] and captured_piece == 0:
        cap_sq = to_sq - 8 if color == Piece.WHITE else to_sq + 8
        undo['ep_capture_sq'] = cap_sq
        undo['captured'] = b.squares[cap_sq]
        b.squares[cap_sq] = 0
        if undo['captured'] != 0:
            b.num_pieces -= 1
            b.active_squares.discard(cap_sq)

    b.active_squares.discard(from_sq)
    if captured_piece != 0:
        b.num_pieces -= 1
        b.active_squares.discard(to_sq)

    b.squares[from_sq] = 0
    if pt == Piece.PAWN:
        if (color == Piece.WHITE and _rank(to_sq) == 7) or (color == Piece.BLACK and _rank(to_sq) == 0):
            promo = promotion if promotion is not None else Piece.QUEEN
            b.squares[to_sq] = (color | promo)
        else:
            b.squares[to_sq] = moved_piece
    else:
        b.squares[to_sq] = moved_piece

    if pt == Piece.PAWN:
        if abs(to_sq - from_sq) == 16:
            b.en_passant = (from_sq + to_sq) // 2

    b.active_squares.add(to_sq)

    if pt == Piece.KING:
        if color == Piece.WHITE:
            b.white_king = to_sq
        else:
            b.black_king = to_sq

    if pt == Piece.KING:
        if from_sq == 4 and to_sq == 6:
            undo['castle_rook_from'] = 7
            undo['castle_rook_to'] = 5
        elif from_sq == 4 and to_sq == 2:
            undo['castle_rook_from'] = 0
            undo['castle_rook_to'] = 3
        elif from_sq == 60 and to_sq == 62:
            undo['castle_rook_from'] = 63
            undo['castle_rook_to'] = 61
        elif from_sq == 60 and to_sq == 58:
            undo['castle_rook_from'] = 56
            undo['castle_rook_to'] = 59

        if undo['castle_rook_from'] is not None:
            rf = undo['castle_rook_from']
            rt = undo['castle_rook_to']
            undo['castle_rook_piece'] = b.squares[rf]
            b.squares[rf] = 0
            b.squares[rt] = undo['castle_rook_piece']
            b.active_squares.discard(rf)
            b.active_squares.add(rt)

    _update_castling_rights(b, from_sq, to_sq, moved_piece, undo['captured'])
    
    b.switch_turn()
    if update_fen:
        b.generate_fen_string()
    return undo

def undo_move(b, undo, update_fen=True):
    from_sq = undo['from']
    to_sq = undo['to']
    b.side_to_move = undo['prev_side']
    b.castling = undo['prev_castling']
    b.en_passant = undo['prev_ep']
    b.halfmove_clock = undo['prev_halfmove']
    b.fullmove_number = undo['prev_fullmove']
    b.num_pieces = undo.get('prev_num_pieces', b.num_pieces)
    b.white_king = undo.get('prev_white_king', b.white_king)
    b.black_king = undo.get('prev_black_king', b.black_king)

    b.squares[from_sq] = undo['moved']
    b.squares[to_sq] = undo['captured']

    b.active_squares.discard(to_sq)
    b.active_squares.add(from_sq)

    if undo['captured'] != 0:
        b.active_squares.add(to_sq)
    else:
        b.active_squares.discard(to_sq)

    if undo['ep_capture_sq'] is not None:
        cap_sq = undo['ep_capture_sq']
        b.squares[to_sq] = 0
        b.squares[cap_sq] = undo['captured']
        b.active_squares.discard(to_sq)
        b.active_squares.add(cap_sq)

    if undo['castle_rook_from'] is not None:
        rf = undo['castle_rook_from']
        rt = undo['castle_rook_to']
        b.squares[rf] = undo['castle_rook_piece']
        b.squares[rt] = 0
        b.active_squares.discard(rt)
        b.active_squares.add(rf)

    if update_fen:
        b.generate_fen_string()

def legal_moves(b, index):
    sq = b.squares[index]
    if sq == 0:
        return []
    color = sq & 24
    if color != b.side_to_move:
        return []

    moves = []
    for from_sq, to_sq, promo in apply_moves(b, index):
        undo = make_move(b, from_sq, to_sq, promo, update_fen=False)
        illegal = is_king_in_check(b, color)
        undo_move(b, undo, update_fen=False)
        if not illegal:
            moves.append(to_sq)
    return moves

def all_legal_moves(b):
    all_moves = []
    active = list(b.active_squares)
    for i in active:
        if b.squares[i] != 0 and (b.squares[i] & 24) == b.side_to_move:
            for to_sq in legal_moves(b, i):
                all_moves.append((i, to_sq))
    return all_moves

# =================================================== #



# ----------------- CHECKS & CASTLING ----------------- #

def is_king_in_check(b, color):
    king_sq = b.white_king if color == Piece.WHITE else b.black_king
    return is_square_attacked(b, king_sq, _opponent(color))

def is_square_attacked(b, index, by_color):
    if by_color == Piece.WHITE:
        pawn_offsets = [7, 9]
    else:
        pawn_offsets = [-7, -9]

    for off in pawn_offsets:
        from_sq = index - off
        if not _in_board(from_sq):
            continue
        if abs(_file(from_sq) - _file(index)) != 1:
            continue
        p = b.squares[from_sq]
        if p != 0 and (p & 24) == by_color and (p & 7) == Piece.PAWN:
            return True

    knight_offsets = [17, 15, 10, 6, -6, -10, -15, -17]
    for off in knight_offsets:
        from_sq = index - off
        if not _in_board(from_sq):
            continue
        fr, ff = _rank(from_sq), _file(from_sq)
        tr, tf = _rank(index), _file(index)
        if not ((abs(fr - tr) == 2 and abs(ff - tf) == 1) or (abs(fr - tr) == 1 and abs(ff - tf) == 2)):
            continue
        p = b.squares[from_sq]
        if p != 0 and (p & 24) == by_color and (p & 7) == Piece.KNIGHT:
            return True

    king_offsets = [9, 8, 7, 1, -1, -7, -8, -9]
    for off in king_offsets:
        from_sq = index - off
        if not _in_board(from_sq):
            continue
        if abs(_file(from_sq) - _file(index)) > 1:
            continue
        p = b.squares[from_sq]
        if p != 0 and (p & 24) == by_color and (p & 7) == Piece.KING:
            return True

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
    for y, x in directions:
        r, f = _rank(index) + y, _file(index) + x
        while 0 <= r < 8 and 0 <= f < 8:
            sq = r * 8 + f
            p = b.squares[sq]
            if p != 0:
                if (p & 24) == by_color:
                    pt = p & 7
                    if y == 0 or x == 0:
                        if pt == Piece.ROOK or pt == Piece.QUEEN:
                            return True
                    else:
                        if pt == Piece.BISHOP or pt == Piece.QUEEN:
                            return True
                break
            r += y
            f += x

    return False

# ====================================================== #