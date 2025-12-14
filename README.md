# Chess Game (Python)

A terminal-based chess game written in Python. The project focuses on clean structure, readable logic, and standard move validation—making it a solid base for adding AI, GUI, or extra chess rules.

---

## Features

- CLI chess board rendering
- Turn-based play (White / Black)
- Coordinate move input (e.g. `e2 e4`)
- Legal move validation (prevents illegal moves)
- Captures and basic rule handling (based on current implementation)
- FEN export for the current position

> This project is designed to be easy to read and extend.

---

## Project Structure

```text
Chess-Game/
├─ game.py          # Main game loop (CLI)
├─ board.py         # Board state + FEN + state utilities
├─ piece.py         # Piece classes / constants
├─ moves.py         # Move generation + legality checks
├─ README.md
└─ LICENSE
