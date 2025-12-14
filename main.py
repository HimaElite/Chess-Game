from board import Board
from piece import Piece
from game import *
from moves import *

######################
## El Clásico Chess ##
######################

def main():
    print("<===================================>")
    print("<= Welcome in the El Clásico Chess =>")
    print("<===================================>")
    print("Here the options to choose from:")
    print("1. Human Vs Human")
    print("2. Human Vs AI")
    print("3. AI Vs AI")
    option = int(input("Choose the number of option you want:"))
    game(option)


if __name__ == "__main__":
    main()