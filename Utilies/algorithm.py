from collections import Counter

from Utilies.piece import Piece
from Utilies.moves import apply_moves, make_move, undo_move, is_king_in_check
from Utilies.terminals_and_evaluations import evaluate

INF = 10 ** 9
MATE = 10 ** 7
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class Algorithm:
    def __init__(self):
        self.nodes = 0
        self.tt = {}
        self.killer_moves = {}
        self.history = {}
        self.max_quiescence_depth = 10
        self.position_counts = Counter()

    def best_move(self, b, depth=4):
        """
        Search using iterative deepening so move ordering gets better every ply.
        Returns: (from_sq, to_sq, promo, score) or None
        """
        self.nodes = 0
        color = b.side_to_move
        legal_moves = self._generate_moves(b)
        if not legal_moves:
            return None

        # keep the real game history so the engine knows when a line reaches
        # a repeated position enough times to be a draw.
        history = getattr(b, "position_history", None)
        if history:
            self.position_counts = Counter(history)
        else:
            self.position_counts = Counter([self._position_key(b)])

        legal_moves = self._order_moves(b, legal_moves, color, 0)
        best = None
        best_score = -INF

        for current_depth in range(1, depth + 1):
            alpha = -INF
            beta = INF
            current_best = None
            current_best_score = -INF

            ordered = legal_moves
            if best is not None:
                ordered = [best] + [m for m in legal_moves if m != best]

            for fr, to, promo in ordered:
                undo = make_move(b, fr, to, promo, update_fen=False)
                if is_king_in_check(b, color):
                    undo_move(b, undo, update_fen=False)
                    continue

                child_key = self._position_key(b)
                self.position_counts[child_key] += 1

                if self.position_counts[child_key] >= 3:
                    score = 0
                else:
                    score = -self.negamax(
                        b,
                        current_depth - 1,
                        -beta,
                        -alpha,
                        ply=1,
                    )

                self.position_counts[child_key] -= 1
                if self.position_counts[child_key] == 0:
                    del self.position_counts[child_key]

                undo_move(b, undo, update_fen=False)

                if score > current_best_score:
                    current_best_score = score
                    current_best = (fr, to, promo)

                if score > alpha:
                    alpha = score

            if current_best is not None:
                best = current_best
                best_score = current_best_score
                legal_moves = [best] + [m for m in legal_moves if m != best]

        if best is None:
            return None

        fr, to, promo = best
        return fr, to, promo, best_score

    def negamax(self, b, depth, alpha, beta, ply):
        self.nodes += 1
        original_alpha = alpha
        color = b.side_to_move
        in_check = is_king_in_check(b, color)
        key = self._position_key(b)

        # same position for the third time => draw
        if self.position_counts.get(key, 0) >= 3:
            return 0

        if in_check and depth > 0:
            depth += 1

        tt_entry = self.tt.get(key)
        if tt_entry is not None and tt_entry["depth"] >= depth:
            tt_score = tt_entry["score"]
            tt_flag = tt_entry["flag"]
            if tt_flag == EXACT:
                return tt_score
            if tt_flag == LOWERBOUND:
                alpha = max(alpha, tt_score)
            elif tt_flag == UPPERBOUND:
                beta = min(beta, tt_score)
            if alpha >= beta:
                return tt_score

        if depth <= 0:
            return self.quiescence(b, alpha, beta, ply)

        moves = self._generate_moves(b)
        if not moves:
            if in_check:
                return -(MATE - ply)
            return 0

        hash_move = tt_entry["best_move"] if tt_entry is not None else None
        moves = self._order_moves(b, moves, color, ply, hash_move)

        best_move = None
        found_legal = False

        for fr, to, promo in moves:
            undo = make_move(b, fr, to, promo, update_fen=False)
            if is_king_in_check(b, color):
                undo_move(b, undo, update_fen=False)
                continue

            found_legal = True
            child_key = self._position_key(b)
            self.position_counts[child_key] += 1

            if self.position_counts[child_key] >= 3:
                score = 0
            else:
                score = -self.negamax(b, depth - 1, -beta, -alpha, ply + 1)

            self.position_counts[child_key] -= 1
            if self.position_counts[child_key] == 0:
                del self.position_counts[child_key]

            undo_move(b, undo, update_fen=False)

            if score > alpha:
                alpha = score
                best_move = (fr, to, promo)

            if alpha >= beta:
                self._store_killer(ply, (fr, to, promo))
                self._store_history(color, fr, to, promo, depth)
                break

        if not found_legal:
            if in_check:
                return -(MATE - ply)
            return 0

        if alpha <= original_alpha:
            flag = UPPERBOUND
        elif alpha >= beta:
            flag = LOWERBOUND
        else:
            flag = EXACT

        self.tt[key] = {
            "depth": depth,
            "score": alpha,
            "flag": flag,
            "best_move": best_move,
        }
        return alpha

    def quiescence(self, b, alpha, beta, ply):
        self.nodes += 1
        color = b.side_to_move
        in_check = is_king_in_check(b, color)

        if not in_check:
            stand_pat = evaluate(b)
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            stand_pat = -INF

        if ply >= self.max_quiescence_depth:
            return stand_pat if stand_pat != -INF else evaluate(b)

        moves = self._generate_moves(b)
        if in_check:
            candidate_moves = moves
        else:
            candidate_moves = [
                m for m in moves
                if self._is_noisy_move(b, m[0], m[1], m[2])
            ]

        candidate_moves = self._order_moves(b, candidate_moves, color, ply)

        for fr, to, promo in candidate_moves:
            undo = make_move(b, fr, to, promo, update_fen=False)
            if is_king_in_check(b, color):
                undo_move(b, undo, update_fen=False)
                continue

            child_key = self._position_key(b)
            self.position_counts[child_key] += 1

            if self.position_counts[child_key] >= 3:
                score = 0
            else:
                score = -self.quiescence(b, -beta, -alpha, ply + 1)

            self.position_counts[child_key] -= 1
            if self.position_counts[child_key] == 0:
                del self.position_counts[child_key]

            undo_move(b, undo, update_fen=False)

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

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

    def _order_moves(self, b, moves, color, ply, hash_move=None):
        if not moves:
            return []

        scored = []
        killer_1, killer_2 = self.killer_moves.get(ply, (None, None))

        for fr, to, promo in moves:
            move = (fr, to, promo)
            score = 0

            if hash_move is not None and move == hash_move:
                score += 1_000_000

            if promo is not None:
                score += 100_000 + (Piece.get_value(promo) or 0)

            captured = b.squares[to]
            if captured != 0:
                attacker = b.squares[fr] & 7
                victim = captured & 7
                score += 50_000 + 10 * (Piece.get_value(victim) or 0) - (Piece.get_value(attacker) or 0)

            if move == killer_1:
                score += 9_000
            elif move == killer_2:
                score += 8_000

            score += self.history.get((color, fr, to, promo), 0)
            scored.append((score, fr, to, promo))

        scored.sort(reverse=True)
        return [(fr, to, promo) for score, fr, to, promo in scored]

    def _is_noisy_move(self, b, fr, to, promo):
        return promo is not None or b.squares[to] != 0

    def _position_key(self, b):
        fen = b.generate_fen_string().split()
        return " ".join(fen[:4])

    def _store_killer(self, ply, move):
        first, second = self.killer_moves.get(ply, (None, None))
        if move != first:
            self.killer_moves[ply] = (move, first)

    def _store_history(self, color, fr, to, promo, depth):
        key = (color, fr, to, promo)
        self.history[key] = self.history.get(key, 0) + depth * depth
