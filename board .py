from piece import Piece

class Board:
    INIT_STATE = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def __init__(self):
        self.squares = [0] * 64
        self.fen_string = Board.INIT_STATE
        self.side_to_move = Piece.WHITE
        self.castling = "KQkq"
        self.en_passant = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.loding_pieces_positions()

    def loding_pieces_positions(self): ### READ fen string
        fen = self.fen_string 
        parts = fen.split()

        placement = parts[0]
        side = parts[1] if len(parts) > 1 else 'w'
        castling = parts[2] if len(parts) > 2 else '-'
        ep = parts[3] if len(parts) > 3 else '-'
        halfmove = parts[4] if len(parts) > 4 else '0'
        fullmove = parts[5] if len(parts) > 5 else '1'

        pieces_dictionary = {'r': Piece.ROOK, 'p': Piece.PAWN, 'n': Piece.KNIGHT,
                             'b': Piece.BISHOP, 'q': Piece.QUEEN, 'k': Piece.KING}

        row = 7
        col = 0
        for char in placement:
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

        self.side_to_move = Piece.WHITE if side == 'w' else Piece.BLACK
        self.castling = castling if castling != '-' else ''
        self.en_passant = None if ep == '-' else self.get_index(ep)
        self.halfmove_clock = int(halfmove)
        self.fullmove_number = int(fullmove)

    def generate_fen_string(self): ### WRITE fen string
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

        if empty_squares:
            row += str(empty_squares)
        rows.append(row)

        placement = "/".join(reversed(rows))
        side = 'w' if self.side_to_move == Piece.WHITE else 'b'
        castling = self.castling if self.castling else '-'
        ep = '-' if self.en_passant is None else self.square_name(self.en_passant)
        self.fen_string = f"{placement} {side} {castling} {ep} {self.halfmove_clock} {self.fullmove_number}"
        return self.fen_string

    def get_index(self, position): ### READ positions like e3
        position = position.lower()
        file = Board.FILES.index(position[0])
        rank = int(position[1]) - 1

        position_index = rank * 8 + file
        return position_index

    def square_name(self, index): ### WRITE positions of index
        file = index % 8
        rank = index // 8
        return f"{Board.FILES[file]}{rank + 1}"

    def switch_turn(self):
        if self.side_to_move == Piece.WHITE:
            self.side_to_move = Piece.BLACK
        else:
            self.side_to_move = Piece.WHITE
            self.fullmove_number += 1

    def present_board(self):
        fen = self.fen_string.split()[0]
        print("   +---+---+---+---+---+---+---+---+")
        print(" 8 ", end="")
        rank = 8
        for char in fen:
            if char == '/':
                rank -= 1
                print("|")
                print("   +---+---+---+---+---+---+---+---+")
                print(f" {rank} ", end="")
            elif char.isdigit():
                for _ in range(int(char)):
                    print("|   ", end="")
            else:
                print("|", char, end=" ")
        print("|")
        print("   +---+---+---+---+---+---+---+---+")
        print("     a   b   c   d   e   f   g   h  ")

def main():
    b = Board()
    b.present_board()
    print(b.generate_fen_string())

if __name__ == "__main__":
    main()
