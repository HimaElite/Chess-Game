from Utilies.board import Board
from Utilies.piece import Piece
from Utilies.moves import *
from Utilies.terminals_and_evaluations import *
from Utilies.algorithm import Algorithm

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

algorithm = Algorithm()


def ensure_position_history(game_board):
    if not hasattr(game_board, "position_history") or not game_board.position_history:
        game_board.position_history = [position_key(game_board)]


def push_current_position(game_board):
    ensure_position_history(game_board)
    game_board.position_history.append(position_key(game_board))


def pop_last_position(game_board):
    ensure_position_history(game_board)
    if len(game_board.position_history) > 1:
        game_board.position_history.pop()


def ai_move(game_board, undo_stack):
    ensure_position_history(game_board)

    color = game_board.side_to_move
    depth = 4 if game_board.num_pieces > 12 else 5
    best = algorithm.best_move(game_board, depth=depth)

    if best is None:
        return undo_stack, "AI has no legal moves!"

    from_sq, to_sq, promo, score = best
    undo = make_move(game_board, from_sq, to_sq, promo)

    if undo:
        undo_stack.append(undo)
        push_current_position(game_board)

    from_name = game_board.square_name(from_sq)
    to_name = game_board.square_name(to_sq)

    if promo is not None:
        promo_name = Piece.get_piece(promo | color).upper()
        the_move = f"AI played piece from {from_name} to {to_name} promoting to {promo_name} (eval={score})"
    else:
        the_move = f"AI played piece from {from_name} to {to_name} (eval={score})"

    current_repetition = repetition_count(game_board)
    if current_repetition > 1:
        the_move += f" [repetition count = {current_repetition}]"

    return undo_stack, the_move


def human_move(game_board, undo_stack, q, option=False):
    ensure_position_history(game_board)

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
                pop_last_position(game_board)

                if option and undo_stack:
                    last = undo_stack.pop()
                    undo_move(game_board, last)
                    pop_last_position(game_board)

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
                    print("Legal moves:", [game_board.square_name(m) for m in moves_list])
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
        if len(parts) >= 3:
            promo = parts[2]
        else:
            promo = None

        undo = take_move(game_board, from_sq, to_sq, promo)
        if undo:
            undo_stack.append(undo)
            push_current_position(game_board)
        return undo_stack, q


def game(option):
    undo_stack = []
    game_board = Board()
    game_board.position_history = [position_key(game_board)]

    final_result = None
    q = False

    while not q:
        game_board.present_board()
        color = Piece.BLACK if game_board.side_to_move == Piece.WHITE else Piece.WHITE

        print(evaluate(game_board))
        t, r = check_terminals(game_board, color)
        if t is not None:
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
