def take_move(self, from_sq, to_sq):
    piece = self.squares[from_sq]
    target = self.squares[to_sq]

    if piece == 0:
        print("No piece at source square!")
        return False

    if target != 0:
        print("Captured:", Piece.get_piece(target))

    self.squares[to_sq] = piece
    self.squares[from_sq] = 0
    return True


def legal_moves(self, index):
    piece = self.squares[index]
    if piece == 0:
        return []

    piece_type = piece & 7
    color = piece & 24
    moves = []

    if piece_type == Piece.PAWN:
        moves = self._pawn_moves(index, color)
    elif piece_type == Piece.KNIGHT:
        moves = self._knight_moves(index, color)
    elif piece_type == Piece.BISHOP:
        moves = self._sliding_moves(index, color, [9, 7, -9, -7])
    elif piece_type == Piece.ROOK:
        moves = self._sliding_moves(index, color, [8, -8, 1, -1])
    elif piece_type == Piece.QUEEN:
        moves = self._sliding_moves(index, color, [8, -8, 1, -1, 9, 7, -9, -7])
    elif piece_type == Piece.KING:
        moves = self._king_moves(index, color)

    return moves