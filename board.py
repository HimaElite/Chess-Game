class Board:
    INIT_STATE = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def __init__(self):
        self.squares = [0] * 64
        self.fen_string = Board.INIT_STATE
        Board.loding_pieces_positions(self)
        
    def loding_pieces_positions(self):
        pieces_dictionary = {'r':Piece.ROOK, 'p':Piece.PAWN, 'n':Piece.KNIGHT,
                             'b':Piece.BISHOP, 'q':Piece.QUEEN, 'k':Piece.KING}
        
        row = 7
        col = 0
        fen = self.fen_string.split()[0]
        for char in fen:
            if char == '/':
                row -= 1
                col = 0
            elif char.isdigit():
                col += int(char)
            else:
                piece_color = Piece.WHITE if char.isupper() else Piece.BLACK
                piece_type = pieces_dictionary[char.lower()]
                self.squares[row * 8 + col] = piece_color | piece_type
                col += 1

    def generate_fen_string(self):
        empty_squares = 0
        rows = []
        row = ""
        for _, square in enumerate(self.squares):
            if _ % 8 == 0 and _ != 0:
                if empty_squares:
                    row += str(empty_squares)
                rows.append(row)
                row = ""
                empty_squares = 0

            p = Piece.get_piece(square)
            if p == '0':
                empty_squares += 1
            else:
                if empty_squares:
                    row += str(empty_squares)
                empty_squares = 0
                row += p
        rows.append(row)

        return "/".join(reversed(rows))
        
    def get_position(self, position):
        position = position.lower()
        file = Board.FILES.index(position[0])
        rank = int(position[1]) - 1

        position_index = rank * 8 + file
        piece_type = Piece.get_piece(self.squares[position_index])
        print("The piece is", piece_type, "in index", position_index)

    def present_squares(self):
        for i in range(8):
            print(self.squares[(7-i) * 8: (7-i) * 8 + 8])

    def present_board(self):
        fen = self.fen_string.split()[0]
        print("+---+---+---+---+---+---+---+---+")
        for char in fen:
            if char == '/':
                print("|")
                print("+---+---+---+---+---+---+---+---+")
            elif char.isdigit():
                for _ in range(int(char)):
                    print("|   ", end="")
            else:
                print("|", char, end=" ")
        print("|")
        print("+---+---+---+---+---+---+---+---+")

class Piece:
    NONE = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

    WHITE = 8
    BLACK = 16

    def get_piece(num):
        pieces = ['0', 'p', 'n', 'b', 'r', 'q', 'k']
        p = pieces[num & 7]
        p = str(p)
        if num & 8:
            return p.upper()
        elif num & 16:
            return p.lower()
        else:
            return '0'

def main():
    b = Board()
    b.present_board()

if __name__ == "__main__":
    main()
    