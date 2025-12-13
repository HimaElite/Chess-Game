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