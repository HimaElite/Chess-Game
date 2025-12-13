from board import Board

def _get_moves(self, index, offsets, color, max_distance=8):
    moves = []
    rank = index // 8
    file = index % 8
    
    for offset in offsets:
        to_sq = index + offset
        
        #  (^^) عشان لو هيخرج برا البورد 
        if to_sq < 0 or to_sq > 63:
            continue
        
        to_rank = to_sq // 8
        to_file = to_sq % 8
        
        # Prevent wrapping around the board
        if abs(file - to_file) > max_distance or abs(rank - to_rank) > max_distance:
            continue
        
        target_piece = self.squares[to_sq]
        target_color = target_piece & 24
        
        # Can't capture own pieces
        if target_piece != 0 and target_color == color:
            continue
        
        moves.append(to_sq)
    
    return moves

def take_move(b: Board, from_sq, to_sq):
    c = b.color_to_move()
    sq = b.squares[b.get_position(from_sq)]

    if sq == 0:
        print("No piece at source square!")
        return False
    
    if (sq & c) != c:
        print("This is the oppenet's square!")
        return False
    
    b.squares[b.get_position(to_sq)] = b.squares[b.get_position(from_sq)]
    b.squares[b.get_position(from_sq)] = 0

def legal_moves(self, index):
    piece = self.squares[index]
    if piece == 0:
        return []

    piece_type = piece & 7
    color = piece & 24
    moves = []

    if piece_type == piece.PAWN:
        moves = self._pawn_moves(index, color)
    elif piece_type == piece.KNIGHT:                        #------------------------------->  Ahmed Hazem
        moves = self._knight_moves(index, color)
    elif piece_type == piece.BISHOP:
        moves = self._sliding_moves(index, color, [9, 7, -9, -7])
    elif piece_type == piece.ROOK:
        moves = self._sliding_moves(index, color, [8, -8, 1, -1])
    elif piece_type == piece.QUEEN:
        moves = self._sliding_moves(index, color, [8, -8, 1, -1, 9, 7, -9, -7])
    elif piece_type == piece.KING:                         #------------------------------->  Ahmed Hazem
        moves = self._king_moves(index, color)

    return moves

def _knight_moves(self, index, color):
    """Generate all legal moves for a knight using shared offset handler."""
    knight_offsets = [17, 15, 10, 6, -6, -10, -15, -17]
    return self._get_moves(index, knight_offsets, color, max_distance=2)

def _king_moves(self, index, color):
    """Generate all legal moves for a king using shared offset handler."""
    king_offsets = [9, 8, 7, 1, -1, -7, -8, -9]
    return self._get_moves(index, king_offsets, color, max_distance=1)