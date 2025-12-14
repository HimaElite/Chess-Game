from board import Board
from piece import Piece
from moves import *
from terminals_and_evaluations import check_terminals
import random as rand

### --------------------------------------------- ###
#   ALL AVALABLE COMMANDS:
#
#   ['q', 'quit', 'exit'] ---> to quit
#   'fen' ---> to get the fen string of the board
#   'undo' ---> to undo your last move
#   'moves position' ---> this will return avalable
#                         moves for this position
#   'position1 position2' ---> to move a piece from
#                              position one to two
### --------------------------------------------- ###

def ai_move(game_board, undo_stack):
    available_moves = all_legal_moves(game_board)
    choice = rand.choice(available_moves)
    from_sq = game_board.square_name(choice[0])
    to_sq = game_board.square_name(choice[1])
    undo = take_move(game_board, from_sq, to_sq)
    if undo:
        undo_stack.append(undo)
    the_move = f"AI played piece from {from_sq} to {to_sq}"
    return undo_stack, the_move


def human_move(game_board, undo_stack, q):
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
    undo_stack = []
    game_board = Board()
    final_result = None
    q = False

    while not q:
        game_board.present_board()
        color = Piece.BLACK if game_board.side_to_move == Piece.WHITE else Piece.WHITE
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
            undo_stack, q = human_move(game_board, undo_stack, q)
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
    for d in range(1, 8):
        print(move_generation_test(game_board, d))


if __name__ == "__main__":
    main()
