from Utilies.board import Board
from Utilies.piece import Piece
from Utilies.game import *
from Utilies.moves import *

######################
## El Clásico Chess ##
######################

def main():
    playing = True
    while playing:
        print("<===================================>")
        print("<= Welcome in the El Clásico Chess =>")
        print("<===================================>")
        print("Here the options to choose from:")
        print("1. Human Vs Human")
        print("2. Human Vs AI")
        print("3. AI Vs AI")
        option = int(input("Choose the number of option you want:"))
        side = None
        if option == 2:
            side = input("Which side you want to play with? (White/Black)")
            if side.lower() == 'white' or side.lower() == 'w':
                side = Piece.WHITE
            else:
                side = Piece.BLACK
        game(option, side)
        p = input("Do you want to play again? (y/n)")
        if p.lower() == 'n' or p.lower() == 'no':
            playing = False


if __name__ == "__main__":
    main()