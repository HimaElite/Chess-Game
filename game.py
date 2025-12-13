from board import Board
from piece import Piece
from moves import *

game_board = Board()
for r in range(6):
    game_board.present_board()
    piece_to_move = input("Enter the position of the piece you want to move:")
    position_to_replace = input("Enter the position you want to replace piece in:")
    take_move(game_board, piece_to_move, position_to_replace)
    print(game_board.generate_fen_string())