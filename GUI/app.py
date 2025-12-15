from flask import Flask, render_template, request, jsonify, session, send_from_directory
from ChessGame.board import Board
from ChessGame.piece import Piece
from ChessGame.moves import take_move, all_legal_moves, legal_moves
from ChessGame.game import ai_move
import random as rand
import os
import time

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'el-clasico-chess-secret'

# Game state storage
games = {}

# Serve images from GUI/images folder
@app.route('/static/images/<filename>')
def serve_images(filename):
    """Serve images from the images folder"""
    images_folder = os.path.join(os.path.dirname(__file__), 'images')
    return send_from_directory(images_folder, filename)

# Serve sounds from GUI/sounds folder
@app.route('/sounds/<path:filename>')
def serve_sounds(filename):
    """Serve sound files from the sounds folder"""
    sounds_folder = os.path.join(os.path.dirname(__file__), 'sounds')
    return send_from_directory(sounds_folder, filename)

# Serve videos from GUI/videos folder
@app.route('/videos/<path:filename>')
def serve_videos(filename):
    """Serve video files from the videos folder"""
    videos_folder = os.path.join(os.path.dirname(__file__), 'videos')
    return send_from_directory(videos_folder, filename)

def get_board_display(board):
    """Convert board state to displayable format with piece symbols and colors"""
    display = []
    piece_symbols = {
        Piece.PAWN: '♟',
        Piece.KNIGHT: '♞',
        Piece.BISHOP: '♝',
        Piece.ROOK: '♜',
        Piece.QUEEN: '♛',
        Piece.KING: '♚'
    }
    
    for i, square in enumerate(board.squares):
        if square == 0:
            display.append({'piece': None, 'color': None})
        else:
            piece_type = square & 7
            color = 'madrid' if square & Piece.WHITE else 'barcelona'
            symbol = piece_symbols.get(piece_type, '?')
            display.append({'piece': symbol, 'color': color, 'type': piece_type})
    
    return display

def get_square_name(index):
    """Convert index (0-63) to chess notation (a1-h8)"""
    file = index % 8
    rank = index // 8
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    return files[file] + str(rank + 1)

def get_square_index(square_name):
    """Convert chess notation (a1-h8) to index (0-63)"""
    file = ord(square_name[0]) - ord('a')
    rank = int(square_name[1]) - 1
    return rank * 8 + file

@app.route('/')
def index():
    return render_template('mode_selector.html')

@app.route('/team-selection')
def team_selection():
    """Show team selection page for Human vs AI"""
    return render_template('team_selector.html')

@app.route('/game/<int:mode>')
def game(mode):
    """Start a new game with selected mode"""
    player_team = request.args.get('team', 'madrid')  # default to madrid (white)
    game_id = rand.randint(100000, 999999)
    games[game_id] = {
        'board': Board(),
        'mode': mode,
        'player_team': player_team,
        'undo_stack': [],
        'game_over': False,
        'winner': None,
        'selected_square': None
    }
    session['game_id'] = game_id
    return render_template('index.html', game_id=game_id, mode=mode, player_team=player_team)

@app.route('/api/board/<int:game_id>')
def get_board(game_id):
    """Get current board state"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_state = games[game_id]
    board = game_state['board']
    
    return jsonify({
        'board': get_board_display(board),
        'side_to_move': 'white' if board.side_to_move == Piece.WHITE else 'black',
        'game_over': game_state['game_over'],
        'winner': game_state['winner'],
        'castling': board.castling,
        'en_passant': board.en_passant
    })

@app.route('/api/legal_moves/<int:game_id>/<square>')
def get_legal_moves_api(game_id, square):
    """Get legal moves for a square"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    try:
        board = games[game_id]['board']
        sq_index = get_square_index(square)
        
        # Check if square has a piece of current player's color
        piece = board.squares[sq_index]
        if piece == 0:
            return jsonify({'legal_moves': []})
        
        if board.side_to_move == Piece.WHITE and not (piece & Piece.WHITE):
            return jsonify({'legal_moves': []})
        if board.side_to_move == Piece.BLACK and not (piece & Piece.BLACK):
            return jsonify({'legal_moves': []})
        
        moves = legal_moves(board, sq_index)
        move_names = [get_square_name(m) for m in moves]
        
        return jsonify({'legal_moves': move_names})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/move/<int:game_id>', methods=['POST'])
def make_move(game_id):
    """Make a move on the board"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    from_sq = data.get('from')
    to_sq = data.get('to')
    promo = data.get('promo')
    
    try:
        game_state = games[game_id]
        board = game_state['board']
        
        # Validate move
        sq_index = get_square_index(from_sq)
        moves = legal_moves(board, sq_index)
        to_index = get_square_index(to_sq)
        
        if to_index not in moves:
            return jsonify({'error': 'Illegal move'}), 400
        
        # Make the move
        undo = take_move(board, from_sq, to_sq, promo)
        if undo:
            game_state['undo_stack'].append(undo)
        
        # Check game over
        if not all_legal_moves(board):
            game_state['game_over'] = True
            game_state['winner'] = 'barcelona' if board.side_to_move == Piece.WHITE else 'madrid'
        
        # For Human vs AI, don't make AI move here - let frontend handle it with thinking animation
        ai_needs_to_move = False
        if game_state['mode'] == 2 and not game_state['game_over']:  # Human vs AI
            player_team = game_state.get('player_team', 'madrid')
            ai_color = Piece.BLACK if player_team == 'madrid' else Piece.WHITE
            
            if board.side_to_move == ai_color:
                ai_needs_to_move = True
        
        return jsonify({
            'success': True,
            'board': get_board_display(board),
            'side_to_move': 'white' if board.side_to_move == Piece.WHITE else 'black',
            'game_over': game_state['game_over'],
            'winner': game_state['winner'],
            'ai_needs_to_move': ai_needs_to_move
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/undo/<int:game_id>', methods=['POST'])
def undo_move(game_id):
    """Undo the last move"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    try:
        from ChessGame.moves import undo_move as undo_chess_move
        
        game_state = games[game_id]
        if game_state['undo_stack']:
            last = game_state['undo_stack'].pop()
            undo_chess_move(game_state['board'], last)
            game_state['game_over'] = False
            game_state['winner'] = None
        
        board = game_state['board']
        return jsonify({
            'success': True,
            'board': get_board_display(board),
            'side_to_move': 'white' if board.side_to_move == Piece.WHITE else 'black'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/ai_move/<int:game_id>', methods=['POST'])
def make_ai_move(game_id):
    """Make an AI move (for AI vs AI mode)"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    try:
        game_state = games[game_id]
        board = game_state['board']
        
        if game_state['game_over']:
            return jsonify({'error': 'Game is over'}), 400
        
        # Count pieces before move
        pieces_before = sum(1 for sq in board.squares if sq != 0)
        print(f"[AI MOVE] Game {game_id}: Pieces before move: {pieces_before}")
        
        # Make AI move
        ai_undo, ai_move_text = ai_move(board, game_state['undo_stack'])
        game_state['undo_stack'] = ai_undo
        
        # Count pieces after move
        pieces_after = sum(1 for sq in board.squares if sq != 0)
        print(f"[AI MOVE] Game {game_id}: Pieces after move: {pieces_after}, Move text: {ai_move_text}")
        
        # Check game over after AI move
        if not all_legal_moves(board):
            game_state['game_over'] = True
            game_state['winner'] = 'barcelona' if board.side_to_move == Piece.WHITE else 'madrid'
        
        board_display = get_board_display(board)
        print(f"[AI MOVE] Game {game_id}: Board display squares with pieces: {sum(1 for sq in board_display if sq['piece'])}")
        
        return jsonify({
            'success': True,
            'board': board_display,
            'side_to_move': 'white' if board.side_to_move == Piece.WHITE else 'black',
            'game_over': game_state['game_over'],
            'winner': game_state['winner'],
            'ai_move': ai_move_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/restart/<int:game_id>', methods=['POST'])
def restart_game(game_id):
    """Restart the game"""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game_state = games[game_id]
    mode = game_state['mode']
    player_team = game_state.get('player_team', 'madrid')
    
    game_state['board'] = Board()
    game_state['undo_stack'] = []
    game_state['game_over'] = False
    game_state['winner'] = None
    
    return jsonify({
        'success': True,
        'board': get_board_display(game_state['board']),
        'side_to_move': 'white'
    })

if __name__ == '__main__':
    app.run(debug=True)
