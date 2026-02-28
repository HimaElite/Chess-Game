from __future__ import annotations

import os
import re
import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory, session

from Utilies.board import Board
from Utilies.piece import Piece
from Utilies.moves import legal_moves, take_move
from Utilies.moves import undo_move as undo_chess_move
from Utilies.game import ai_move as engine_ai_move
from Utilies.terminals_and_evaluations import check_terminals


# ------------------------- Config ------------------------- #

APP_SECRET_KEY = os.getenv("CHESS_SECRET_KEY", "el-clasico-chess-secret")

app = Flask(__name__, template_folder="GUI/templates", static_folder="GUI/static")
app.secret_key = APP_SECRET_KEY

# Cache static files (css/js) for 1 day (safe for dev; browsers revalidate)
app.config.setdefault("SEND_FILE_MAX_AGE_DEFAULT", 60 * 60 * 24)
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

SQUARE_RE = re.compile(r"^[a-h][1-8]$")

# Team theme (kept from existing UI)
TEAM_WHITE = "madrid"       # white side
TEAM_BLACK = "barcelona"    # black side

PIECE_SYMBOLS = {
    Piece.PAWN: "♟",
    Piece.KNIGHT: "♞",
    Piece.BISHOP: "♝",
    Piece.ROOK: "♜",
    Piece.QUEEN: "♛",
    Piece.KING: "♚",
}

DISPLAY_ORDER: List[int] = [(7 - r) * 8 + c for r in range(8) for c in range(8)]
BOARD_TO_DISPLAY: List[int] = [0] * 64
for ui_i, b_i in enumerate(DISPLAY_ORDER):
    BOARD_TO_DISPLAY[b_i] = ui_i


# ---------------------- Game storage ---------------------- #

@dataclass
class GameState:
    board: Board = field(default_factory=Board)
    mode: int = 1
    player_team: str = TEAM_WHITE
    undo_stack: List[dict] = field(default_factory=list)

    # terminal state
    game_over: bool = False
    terminal: Optional[int] = None  # 1 white win, -1 black win, 0 draw, None ongoing
    result_text: Optional[str] = None

    created_at: float = field(default_factory=time.time)
    last_access: float = field(default_factory=time.time)


class GameStore:
    """Simple in-memory store with TTL cleanup."""

    def __init__(self, ttl_seconds: int = 2 * 60 * 60, max_games: int = 200):
        self.ttl = ttl_seconds
        self.max_games = max_games
        self._lock = threading.RLock()
        self._games: Dict[int, GameState] = {}

    def _now(self) -> float:
        return time.time()

    def cleanup(self) -> None:
        now = self._now()
        with self._lock:
            expired = [gid for gid, g in self._games.items() if (now - g.last_access) > self.ttl]
            for gid in expired:
                self._games.pop(gid, None)

            if len(self._games) <= self.max_games:
                return
            items = sorted(self._games.items(), key=lambda kv: kv[1].last_access)
            for gid, _ in items[: max(0, len(self._games) - self.max_games)]:
                self._games.pop(gid, None)

    def create(self, mode: int, player_team: str) -> int:
        with self._lock:
            for _ in range(50):
                gid = secrets.randbelow(900000) + 100000
                if gid not in self._games:
                    gs = GameState(mode=mode, player_team=player_team)
                    _sync_board_counters(gs.board)
                    _update_terminal(gs)
                    self._games[gid] = gs
                    return gid
        raise RuntimeError("Failed to allocate game id")

    def get(self, gid: int) -> Optional[GameState]:
        with self._lock:
            gs = self._games.get(gid)
            if gs:
                gs.last_access = self._now()
            return gs


games = GameStore()


@app.before_request
def _cleanup_games_periodically() -> None:
    games.cleanup()


# ------------------------- Helpers ------------------------- #

def _sync_board_counters(board: Board) -> None:
    """Fixes missing initial counters used by evaluation/AI depth."""
    try:
        board.num_pieces = len(board.active_squares)
    except Exception:
        pass


def _piece_dict(square_value: int) -> dict:
    if square_value == 0:
        return {"piece": None, "color": None}

    piece_type = square_value & 7
    is_white = bool(square_value & Piece.WHITE)
    team = TEAM_WHITE if is_white else TEAM_BLACK
    return {"piece": PIECE_SYMBOLS.get(piece_type, "?"), "color": team, "type": piece_type}


def get_board_display(board: Board) -> List[dict]:
    """Flat list in engine index order (0=a1 .. 63=h8)."""
    return [_piece_dict(v) for v in board.squares]


def get_board_display_ui(board: Board) -> List[dict]:
    """Flat list in UI order (0=a8 .. 63=h1), i.e. white at bottom."""
    return [_piece_dict(board.squares[i]) for i in DISPLAY_ORDER]


def get_square_name(index: int) -> str:
    files = "abcdefgh"
    return files[index % 8] + str(index // 8 + 1)


def get_square_index(square_name: str) -> int:
    files = "abcdefgh"
    return (int(square_name[1]) - 1) * 8 + files.index(square_name[0])


def _validate_square(s: str) -> bool:
    return isinstance(s, str) and bool(SQUARE_RE.match(s.strip().lower()))


def _update_terminal(gs: GameState) -> None:
    b = gs.board
    last_mover = Piece.BLACK if b.side_to_move == Piece.WHITE else Piece.WHITE
    t, reason = check_terminals(b, last_mover)
    gs.terminal = t
    gs.result_text = reason
    gs.game_over = (t is not None)


def _winner_team(gs: GameState) -> Optional[str]:
    if gs.terminal is None:
        return None
    if gs.terminal == 1:
        return TEAM_WHITE
    if gs.terminal == -1:
        return TEAM_BLACK
    return "draw"


def _ai_needs_to_move(gs: GameState) -> bool:
    if gs.mode != 2 or gs.game_over:
        return False
    ai_color = Piece.BLACK if gs.player_team == TEAM_WHITE else Piece.WHITE
    return gs.board.side_to_move == ai_color


# ----------------------- Static routes ----------------------- #

@app.route("/static/images/<path:filename>")
def serve_images(filename: str):
    images_folder = os.path.join(os.path.dirname(__file__), "GUI", "images")
    return send_from_directory(images_folder, filename)


@app.route("/sounds/<path:filename>")
def serve_sounds(filename: str):
    sounds_folder = os.path.join(os.path.dirname(__file__), "GUI", "sounds")
    return send_from_directory(sounds_folder, filename)


@app.route("/videos/<path:filename>")
def serve_videos(filename: str):
    videos_folder = os.path.join(os.path.dirname(__file__), "GUI", "videos")
    return send_from_directory(videos_folder, filename)


# ------------------------- Pages ------------------------- #

@app.route("/")
def index():
    return render_template("mode_selector.html")


@app.route("/team-selection")
def team_selection():
    return render_template("team_selector.html")


@app.route("/game/<int:mode>")
def game(mode: int):
    player_team = request.args.get("team", TEAM_WHITE)
    if player_team not in (TEAM_WHITE, TEAM_BLACK):
        player_team = TEAM_WHITE

    game_id = games.create(mode=mode, player_team=player_team)
    session["game_id"] = game_id

    return render_template(
        "index.html",
        game_id=game_id,
        mode=mode,
        player_team=player_team,
        display_order=DISPLAY_ORDER,
    )


# ------------------------- API ------------------------- #

@app.get("/api/board/<int:game_id>")
def api_board(game_id: int):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    b = gs.board
    return jsonify({
        "board": get_board_display(b),
        "board_ui": get_board_display_ui(b),
        "display_order": DISPLAY_ORDER,
        "board_to_display": BOARD_TO_DISPLAY,
        "side_to_move": "white" if b.side_to_move == Piece.WHITE else "black",
        "game_over": gs.game_over,
        "winner": _winner_team(gs),
        "result_text": gs.result_text,
        "castling": b.castling,
        "en_passant": b.en_passant,
    })


@app.get("/api/legal_moves/<int:game_id>/<square>")
def api_legal_moves(game_id: int, square: str):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    square = square.strip().lower()
    if not _validate_square(square):
        return jsonify({"legal_moves": []})

    b = gs.board
    try:
        from_index = get_square_index(square)
    except Exception:
        return jsonify({"legal_moves": []})

    piece = b.squares[from_index]
    if piece == 0 or (piece & 24) != b.side_to_move:
        return jsonify({"legal_moves": []})

    moves = legal_moves(b, from_index)
    return jsonify({"legal_moves": [get_square_name(m) for m in moves]})


@app.post("/api/move/<int:game_id>")
def api_move(game_id: int):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404
    if gs.game_over:
        return jsonify({"error": "Game is over"}), 400

    data = request.get_json(silent=True) or {}
    from_sq = (data.get("from") or "").strip().lower()
    to_sq = (data.get("to") or "").strip().lower()
    promo = data.get("promo")

    if not (_validate_square(from_sq) and _validate_square(to_sq)):
        return jsonify({"error": "Invalid squares"}), 400

    b = gs.board
    try:
        from_index = get_square_index(from_sq)
        to_index = get_square_index(to_sq)
    except Exception:
        return jsonify({"error": "Invalid squares"}), 400

    if to_index not in legal_moves(b, from_index):
        return jsonify({"error": "Illegal move"}), 400

    undo = take_move(b, from_sq, to_sq, promo)
    if not undo:
        return jsonify({"error": "Illegal move"}), 400

    gs.undo_stack.append(undo)
    _sync_board_counters(b)
    _update_terminal(gs)

    return jsonify({
        "success": True,
        "board": get_board_display(b),
        "board_ui": get_board_display_ui(b),
        "side_to_move": "white" if b.side_to_move == Piece.WHITE else "black",
        "game_over": gs.game_over,
        "winner": _winner_team(gs),
        "result_text": gs.result_text,
        "ai_needs_to_move": _ai_needs_to_move(gs),
    })


@app.post("/api/undo/<int:game_id>")
def api_undo(game_id: int):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    if not gs.undo_stack:
        b = gs.board
        return jsonify({
            "success": True,
            "board": get_board_display(b),
            "board_ui": get_board_display_ui(b),
            "side_to_move": "white" if b.side_to_move == Piece.WHITE else "black",
            "game_over": gs.game_over,
            "winner": _winner_team(gs),
        })

    # Human vs AI: undo two plies when possible
    plies = 2 if (gs.mode == 2 and len(gs.undo_stack) >= 2) else 1
    for _ in range(plies):
        if not gs.undo_stack:
            break
        last = gs.undo_stack.pop()
        undo_chess_move(gs.board, last)

    _sync_board_counters(gs.board)
    _update_terminal(gs)

    b = gs.board
    return jsonify({
        "success": True,
        "board": get_board_display(b),
        "board_ui": get_board_display_ui(b),
        "side_to_move": "white" if b.side_to_move == Piece.WHITE else "black",
        "game_over": gs.game_over,
        "winner": _winner_team(gs),
        "result_text": gs.result_text,
    })


@app.post("/api/ai_move/<int:game_id>")
def api_ai_move(game_id: int):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404
    if gs.game_over:
        return jsonify({"error": "Game is over"}), 400

    if gs.mode == 2 and not _ai_needs_to_move(gs):
        return jsonify({"error": "Not AI turn"}), 400
    if gs.mode == 1:
        return jsonify({"error": "AI not enabled in this mode"}), 400

    b = gs.board
    new_stack, text = engine_ai_move(b, gs.undo_stack)
    gs.undo_stack = new_stack

    _sync_board_counters(b)
    _update_terminal(gs)

    return jsonify({
        "success": True,
        "board": get_board_display(b),
        "board_ui": get_board_display_ui(b),
        "side_to_move": "white" if b.side_to_move == Piece.WHITE else "black",
        "game_over": gs.game_over,
        "winner": _winner_team(gs),
        "result_text": gs.result_text,
        "ai_move": text,
    })


@app.post("/api/restart/<int:game_id>")
def api_restart(game_id: int):
    gs = games.get(game_id)
    if not gs:
        return jsonify({"error": "Game not found"}), 404

    gs.board = Board()
    gs.undo_stack = []
    _sync_board_counters(gs.board)
    _update_terminal(gs)

    b = gs.board
    return jsonify({
        "success": True,
        "board": get_board_display(b),
        "board_ui": get_board_display_ui(b),
        "side_to_move": "white",
        "game_over": gs.game_over,
        "winner": _winner_team(gs),
        "result_text": gs.result_text,
    })


if __name__ == "__main__":
    # Use: CHESS_HOST=0.0.0.0 CHESS_PORT=5000 CHESS_DEBUG=1 python app.py
    host = os.getenv("CHESS_HOST", "127.0.0.1")
    port = int(os.getenv("CHESS_PORT", "5000"))
    debug = os.getenv("CHESS_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)