# ♟️ El Clásico Chess

A chess game inspired by the rivalry between **Real Madrid** and **FC Barcelona**, built with **Python, Flask, HTML, CSS, and JavaScript**.

The project combines a browser-based chess interface with a custom chess engine that uses **Minimax and Alpha-Beta Pruning** to make decisions. It was developed as a university AI project to explore game logic, search algorithms, and heuristic evaluation.

## Features

- **Three game modes:** Human vs Human, Human vs AI, and AI vs AI.
- **El Clásico theme:** Real Madrid plays White and Barcelona plays Black. Choose your team when playing against the AI.
- **Interactive board:** Select a piece and see its available legal moves highlighted.
- **Chess rules:** Legal move validation, castling, en passant, pawn promotion, check, checkmate, and stalemate.
- **Game controls:** Undo moves, restart the game, or return to the main menu.
- **Game feedback:** Turn indicator, last-move display, winner announcement, and sound effects.
- **Custom AI:** Searches possible moves and evaluates positions rather than choosing randomly.

> **Note:** In the web interface, pawns are automatically promoted to a queen. The game runs locally in your browser; it does not provide online multiplayer.

## How the AI Works

The chess AI is implemented in Python without relying on an external chess engine.

1. **Move generation:** Generate possible moves and filter out moves that would leave the king in check.
2. **Minimax search:** Explore future moves to choose a strong response, using a negamax-style implementation.
3. **Alpha-Beta Pruning:** Skip branches that cannot improve the current best result.
4. **Move ordering:** Prioritize captures and pawn promotions to help the search run more efficiently.
5. **Position evaluation:** Score board positions using material values, piece-square tables, bishop pairs, rook activity, and passed pawns.

The AI currently searches **4 plies** when more than 12 pieces remain and **5 plies** in positions with 12 or fewer pieces.

## Technologies

| Technology | Purpose |
| --- | --- |
| Python | Chess rules, game state, and AI engine |
| Flask | Web server and game API |
| HTML & CSS | Game pages, board layout, and El Clásico styling |
| JavaScript | Board interactions, legal-move highlights, and API requests |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/HimaElite/Chess-Game.git
cd Chess-Game
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the web application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## How to Play

1. Select **Human vs Human**, **Human vs AI**, or **AI vs AI** on the main menu.
2. Choose a team to start the match. Real Madrid represents White and Barcelona represents Black.
3. In a human-controlled game, click one of your pieces, then click a highlighted square to move it.
4. Use **Undo Move** or **Restart Game** whenever needed.
5. In **AI vs AI** mode, watch the two computer-controlled sides play automatically.

## Project Structure

```text
Chess-Game/
├── app.py                          # Flask application and game API
├── requirements.txt
├── GUI/
│   ├── templates/
│   │   ├── mode_selector.html      # Game mode and team selection
│   │   ├── team_selector.html      # Additional team selection page
│   │   └── index.html              # Chessboard and gameplay interface
│   ├── static/css/style.css        # Interface styling
│   ├── images/                     # Team logos and background assets
│   └── sounds/                     # Move and game sound effects
├── Utilies/
│   ├── algorithm.py                # Minimax and Alpha-Beta Pruning
│   ├── board.py                    # Board representation and FEN support
│   ├── game.py                     # Game flow and AI move integration
│   ├── moves.py                    # Move generation and validation
│   ├── piece.py                    # Piece definitions and values
│   ├── terminals_and_evaluations.py # Endgame checks and evaluation
│   └── main.py                     # Earlier terminal interface entry point
├── README.md
└── LICENSE.md
```

## License

This project is released under the **MIT License**. See [LICENSE.md](LICENSE.md) for details.
