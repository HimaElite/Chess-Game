from board import Board
from piece import Piece
from moves import *
from terminals_and_evaluations import *
import random as rand

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

INF = 10**9

def minmax(game_board, depth, alpha=-INF, beta=INF):
    if depth == 0:
        return evaluate(game_board)

    best_eval = -INF
    color = game_board.side_to_move
    active = list(game_board.active_squares)
    has_legal = False
    for i in active:
        sq = game_board.squares[i]
        if (sq & 24) != color:
            continue

        for from_sq, to_sq, promo in apply_moves(game_board, i):
            undo = make_move(game_board, from_sq, to_sq, promo, update_fen=False)
            if is_king_in_check(game_board, color):
                undo_move(game_board, undo, update_fen=False)
                continue
            has_legal = True
            evaluation = -minmax(game_board, depth - 1, -beta, -alpha)
            undo_move(game_board, undo, update_fen=False)

            if evaluation > best_eval:
                best_eval = evaluation

            if best_eval > alpha:
                alpha = best_eval

            if alpha >= beta:
                return best_eval

    if not has_legal:
        if is_king_in_check(game_board, color):
            return -INF
        return 0

    return best_eval

def ai_move(game_board, undo_stack):
    best_eval = -INF
    best_move = None

    color = game_board.side_to_move
    active = list(game_board.active_squares)

    for i in active:
        sq = game_board.squares[i]
        if (sq & 24) != color:
            continue

        for from_sq, to_sq, promo in apply_moves(game_board, i):
            undo = make_move(game_board, from_sq, to_sq, promo, update_fen=False)

            if is_king_in_check(game_board, color):
                undo_move(game_board, undo, update_fen=False)
                continue

            evaluation = -minmax(game_board, 3)

            undo_move(game_board, undo, update_fen=False)

            if evaluation > best_eval:
                best_eval = evaluation
                best_move = (from_sq, to_sq, promo)

    if best_move is None:
        return undo_stack, "AI has no legal moves!"

    from_sq, to_sq, promo = best_move
    undo = make_move(game_board, from_sq, to_sq, promo)
    if undo:
        undo_stack.append(undo)

    from_name = game_board.square_name(from_sq)
    to_name = game_board.square_name(to_sq)

    if promo is not None:
        promo_name = Piece.get_piece(promo | color).upper()
        the_move = f"AI played piece from {from_name} to {to_name} promoting to {promo_name}"
    else:
        the_move = f"AI played piece from {from_name} to {to_name}"
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
        print(get_evaluation(game_board))

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
