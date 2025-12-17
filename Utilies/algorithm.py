from Utilies.piece import Piece
from Utilies.moves import apply_moves, make_move, undo_move, is_king_in_check
from Utilies.terminals_and_evaluations import evaluate

INF = 10**9
MATE = 10**7

class Algorithm:
    def __init__(self):
        self.nodes = 0

    def best_move(self, b, depth=3):
        self.nodes = 0
        color = b.side_to_move

        best = None
        best_score = -INF

        moves = self._generate_moves(b)
        if not moves:
            return None

        moves = self._order_moves(b, moves)

        alpha = -INF
        beta = INF
        for fr, to, promo in moves:
            undo = make_move(b, fr, to, promo, update_fen=False)
            if is_king_in_check(b, color):
                undo_move(b, undo, update_fen=False)
                continue

            score = -self.minimax(b, depth - 1, -beta, -alpha, ply=1)
            undo_move(b, undo, update_fen=False)

            if score > best_score:
                best_score = score
                best = (fr, to, promo)

            if score > alpha:
                alpha = score

        if best is None:
            return None

        fr, to, promo = best
        return fr, to, promo, best_score

    def minimax(self, b, depth, alpha, beta, ply):
        self.nodes += 1

        if depth <= 0:
            return evaluate(b)

        color = b.side_to_move
        moves = self._generate_moves(b)
        if not moves:
            if is_king_in_check(b, color):
                return -(MATE - ply)
            return 0

        moves = self._order_moves(b, moves)

        for fr, to, promo in moves:
            undo = make_move(b, fr, to, promo, update_fen=False)
            if is_king_in_check(b, color):
                undo_move(b, undo, update_fen=False)
                continue

            score = -self.minimax(b, depth - 1, -beta, -alpha, ply + 1)
            undo_move(b, undo, update_fen=False)

            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        return alpha

    def _generate_moves(self, b):
        color = b.side_to_move
        moves = []

        for sq in list(b.active_squares):
            p = b.squares[sq]
            if p == 0 or (p & 24) != color:
                continue

            for fr, to, promo in apply_moves(b, sq):
                moves.append((fr, to, promo))

        return moves

    def _order_moves(self, b, moves):
        scored = []
        for fr, to, promo in moves:
            scored.append((self._move_score(b, fr, to, promo), fr, to, promo))
        scored.sort(reverse=True)
        return [(fr, to, promo) for _, fr, to, promo in scored]

    def _move_score(self, b, fr, to, promo):
        score = 0

        if promo is not None:
            score += 10000 + (Piece.get_value(promo) or 0)

        captured = b.squares[to]
        if captured != 0:
            score += 5000 + (Piece.get_value(captured & 7) or 0)

        return score
