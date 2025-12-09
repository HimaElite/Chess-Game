# ♟️ Python Chess Game

A fully playable **Chess Game built in Python**, featuring a clean object-oriented structure, legal move validation, check/checkmate detection, and customizable AI (Minimax with optional Alpha-Beta pruning).  
This project is ideal for learning game development, search algorithms, and board evaluation techniques.

---

## 🚀 Features

- ✔️ Full chess rules implementation  
- ✔️ Move legality checks (pins, checks, castling, en passant, promotions)  
- ✔️ Undo/redo system  
- ✔️ Simple CLI interface (GUI planned)  
- ✔️ AI engine using **Minimax + Alpha-Beta pruning**  
- ✔️ Modular OOP architecture  
- ✔️ Easily extendable for GUI (Tkinter / PyGame)

---

## 🧠 AI Algorithms Used

- **Minimax** for decision making  
- **Alpha-Beta Pruning** for optimization  
- Optional **heuristic evaluation function** for mid-game decisions  
- Adjustable search depth for performance tuning  

---

## 📁 Project Structure

chess-game/
│
├── src/
│ ├── board.py
│ ├── game.py
│ ├── pieces/
│ │ ├── base.py
│ │ ├── pawn.py
│ │ ├── rook.py
│ │ ├── knight.py
│ │ ├── bishop.py
│ │ ├── queen.py
│ │ └── king.py
│ ├── ai/
│ │ ├── minimax.py
│ │ ├── evaluation.py
│ │ └── utils.py
│ └── utils/
│ └── helpers.py
│
├── README.md
└── LICENSE
