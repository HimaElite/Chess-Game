########## `_get_moves` Function Made By Ahmed Hazem ##########
###### تنفع لكل القطع ####
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

##############------------------------------------------------------###########

def take_move(self, from_sq, to_sq):
    piece = self.squares[from_sq]
    target = self.squares[to_sq]

    if piece == 0:
        print("No piece at source square!")
        return False

    if target != 0:
        print("Captured:", piece.get_piece(target))

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

########## Moves Section Made By Ahmed Hazem ##########

def _knight_moves(self, index, color):
    """Generate all legal moves for a knight using shared offset handler."""
    knight_offsets = [17, 15, 10, 6, -6, -10, -15, -17]
    return self._get_moves(index, knight_offsets, color, max_distance=2)


def _king_moves(self, index, color):
    """Generate all legal moves for a king using shared offset handler."""
    king_offsets = [9, 8, 7, 1, -1, -7, -8, -9]
    return self._get_moves(index, king_offsets, color, max_distance=1)