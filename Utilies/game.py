from board import Board
from piece import Piece
from moves import *
from terminals_and_evaluations import *
# from algorithm import Algorithm

### --------------------------------------------- ###
#   ALL AVALABLE COMMANDS:
#
#   ['q', 'quit', 'exit'] ---> to quit
#   'fen' ---> to get the fen string of the board
#   'undo' ---> to undo your last move
#   'all moves' ---> it gives you all legal moves
#   'moves position' ---> this will return avalable
#                         moves for this position
#   'position1 position2' ---> to move a piece from
#                              position one to two
### --------------------------------------------- ###

# algorithm = Algorithm()
INF = 10**9

def ai_move(game_board, undo_stack):
    MATE_SCORE = 100000
    INF = 10**9

    def _insufficient_material(b):
        if b.num_pieces <= 3:
            minor = 0
            for sq in b.active_squares:
                p = b.squares[sq]
                if p == 0:
                    continue
                pt = p & 7
                if pt == Piece.BISHOP or pt == Piece.KNIGHT:
                    minor += 1
                elif pt != Piece.KING:
                    return False
            return minor <= 1
        return False

    def _move_order_key(b, mv):
        from_sq, to_sq, promo = mv
        moved = b.squares[from_sq]
        captured = b.squares[to_sq]
        score = 0
        if captured != 0:
            score += 1000
        if (moved & 7) == Piece.PAWN and b.en_passant is not None and to_sq == b.en_passant and captured == 0:
            score += 1000
        if promo is not None:
            score += 800
        return score

    def minmax(b, depth, alpha, beta, ply):
        if b.halfmove_clock >= 50:
            return 0
        if _insufficient_material(b):
            return 0

        if depth <= 0:
            return evaluate(b)

        moves = all_legal_moves(b)
        if not moves:
            if is_king_in_check(b, b.side_to_move):
                return -MATE_SCORE + ply
            return 0

        moves.sort(key=lambda m: _move_order_key(b, m), reverse=True)

        best = -INF
        for from_sq, to_sq, promo in moves:
            undo = make_move(b, from_sq, to_sq, promo, update_fen=False)
            score = -minmax(b, depth - 1, -beta, -alpha, ply + 1)
            undo_move(b, undo, update_fen=False)

            if score > best:
                best = score

            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return best

    if game_board.num_pieces <= 10:
        depth = 5
    elif game_board.num_pieces <= 18:
        depth = 4
    else:
        depth = 3

    root_moves = all_legal_moves(game_board)
    if not root_moves:
        return undo_stack, "AI has no legal moves"

    root_moves.sort(key=lambda m: _move_order_key(game_board, m), reverse=True)

    best_move = root_moves[0]
    best_score = -INF
    alpha = -INF
    beta = INF

    for mv in root_moves:
        from_sq, to_sq, promo = mv
        undo = make_move(game_board, from_sq, to_sq, promo, update_fen=False)
        score = -minmax(game_board, depth - 1, -beta, -alpha, 1)
        undo_move(game_board, undo, update_fen=False)

        if score > best_score:
            best_score = score
            best_move = mv

        if score > alpha:
            alpha = score

    from_sq, to_sq, promo = best_move
    undo = make_move(game_board, from_sq, to_sq, promo, update_fen=True)
    if undo:
        undo_stack.append(undo)

    from_name = game_board.square_name(from_sq)
    to_name = game_board.square_name(to_sq)
    if promo is not None:
        promo_name = 'q' if promo == Piece.QUEEN else ('r' if promo == Piece.ROOK else ('b' if promo == Piece.BISHOP else 'n'))
        the_move = f"AI played {from_name} to {to_name}={promo_name} (eval {best_score})"
    else:
        the_move = f"AI played piece from {from_name} to {to_name} (eval {best_score})"

    return undo_stack, the_move

def human_move(game_board, undo_stack, q, option=False):
    while True:
        cmd = input("Enter the move or command: ").strip()
        if not cmd:
            print("You should enter something!")
            continue

        cmd = cmd.lower()
        if cmd in ['q', 'quit', 'exit']:
            q = True
            return undo_stack, q

        if cmd == 'fen':
            print(game_board.generate_fen_string())
            continue

        if cmd == 'undo':
            if undo_stack:
                last = undo_stack.pop()
                undo_move(game_board, last)
                if option:
                    last = undo_stack.pop()
                    undo_move(game_board, last)
                return undo_stack, q
            else:
                print("Nothing to undo")
            continue

        if cmd.startswith('moves'):
            parts = cmd.split()
            if len(parts) == 2:
                try:
                    sq = game_board.get_index(parts[1])
                    moves_list = legal_moves(game_board, sq)
                    print("Legal moves:", [
                          game_board.square_name(m) for m in moves_list])
                except Exception:
                    print("Invalid square!")
            else:
                print("Usage: moves 'position'")
            continue

        if cmd == 'all moves':
            print(all_legal_moves(game_board))
            continue

        parts = cmd.split()
        if len(parts) < 2:
            print("Enter move like: e2 e4")
            continue

        from_sq = parts[0]
        to_sq = parts[1]
        if len(parts) >= 3:  # this is only for pawns
            promo = parts[2]
        else:
            promo = None

        undo = take_move(game_board, from_sq, to_sq, promo)
        if undo:
            undo_stack.append(undo)

        return undo_stack, q

def game(option):
    # start the game
    undo_stack = []
    game_board = Board()
    final_result = None
    q = False

    while not q:
        game_board.present_board()
        color = Piece.BLACK if game_board.side_to_move == Piece.WHITE else Piece.WHITE
        print(evaluate(game_board))

        t, r = check_terminals(game_board, color)
        if t != None:
            if t == 0:
                final_result = f"This is draw because {r}"
            else:
                final_result = r
            break

        side = 'WHITE' if game_board.side_to_move == Piece.WHITE else 'BLACK'
        print("Turn:", side)

        if option == 1:
            undo_stack, q = human_move(game_board, undo_stack, q)
            continue
        elif option == 2 and side == 'WHITE':
            undo_stack, q = human_move(game_board, undo_stack, q, option=True)
            continue
        elif option == 2 and side == 'BLACK':
            undo_stack, the_move = ai_move(game_board, undo_stack)
            print(the_move)
            continue
        elif option == 3:
            undo_stack, the_move = ai_move(game_board, undo_stack)
            print(the_move)
            continue

    print(final_result)


def main():
    game_board = Board()
    for d in range(1, 6):
        print(move_generation_test(game_board, d))


if __name__ == "__main__":
    main()
