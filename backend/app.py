import json
from flask import Flask, jsonify, request
import chess.pgn
import chess.engine
import sqlite3
from datetime import datetime
import time
import os
import statistics
from typing import List, Dict, Any, Optional
import multiprocessing
import threading
from flask_cors import CORS


app = Flask(__name__)

CORS(app)  # Add this right after creating your Flask app

class ChessAnalyzer:
    def __init__(self):
        self.engine_path = "./stockfish"
        self.db_path = "./chess_games.db"
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    pgn TEXT NOT NULL,
                    white TEXT,
                    black TEXT,
                    date TEXT,
                    result TEXT,
                    analyzed BOOLEAN DEFAULT 0,
                    analysis_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mistakes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    move_number INTEGER,
                    fen_before TEXT,
                    fen_after TEXT,
                    player_color TEXT,
                    eval_before REAL,
                    eval_after REAL,
                    eval_diff REAL,
                    mistake_type TEXT,
                    clock_time REAL,
                    FOREIGN KEY(game_id) REFERENCES games(id)
                )
            """)
    
    def import_pgn(self, pgn_text: str) -> Dict[str, Any]:
        game = chess.pgn.read_game(pgn_text)
        game_id = self._generate_game_id(game)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO games VALUES (?, ?, ?, ?, ?, ?, 0, NULL)",
                (game_id, pgn_text, game.headers.get("White"), 
                 game.headers.get("Black"), game.headers.get("Date"),
                 game.headers.get("Result"))
            )
        return {"status": "success", "game_id": game_id}
    
    def analyze_game(self, game_id: str, depth: int = 18) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            pgn = conn.execute(
                "SELECT pgn FROM games WHERE id = ?", (game_id,)
            ).fetchone()[0]
        
        game = chess.pgn.read_game(pgn)
        board = game.board()
        
        engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        analysis = {
            "mistakes": [],
            "summary": {
                "white_mistakes": 0,
                "black_mistakes": 0,
                "worst_mistake": None,
                "critical_moments": []
            }
        }
        
        max_eval_diff = 0
        worst_mistake = None
        
        for node in game.mainline():
            move = node.move
            player = "white" if board.turn == chess.WHITE else "black"
            
            # Get clock time if available
            clock_time = node.clock() if hasattr(node, "clock") else None
            
            # Evaluate position before move
            info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
            eval_before = info_before["score"].white().score(mate_score=10000)
            
            board.push(move)
            
            # Evaluate position after move
            info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
            eval_after = info_after["score"].white().score(mate_score=10000)
            
            eval_diff = abs(eval_after - eval_before)
            
            # Classify mistake
            mistake_type = None
            if eval_diff > 200:
                mistake_type = "blunder"
            elif eval_diff > 100:
                mistake_type = "mistake"
            elif eval_diff > 50:
                mistake_type = "inaccuracy"
            
            if mistake_type:
                mistake = {
                    "move_number": board.fullmove_number,
                    "player": player,
                    "fen_before": board.fen(),
                    "fen_after": board.fen(),
                    "eval_before": eval_before,
                    "eval_after": eval_after,
                    "eval_diff": eval_diff,
                    "mistake_type": mistake_type,
                    "clock_time": clock_time,
                    "move_san": board.san(move)
                }
                
                analysis["mistakes"].append(mistake)
                
                if player == "white":
                    analysis["summary"]["white_mistakes"] += 1
                else:
                    analysis["summary"]["black_mistakes"] += 1
                
                if eval_diff > max_eval_diff:
                    max_eval_diff = eval_diff
                    worst_mistake = mistake
        
        engine.quit()
        
        analysis["summary"]["worst_mistake"] = worst_mistake
        analysis["summary"]["critical_moments"] = self._find_critical_moments(analysis["mistakes"])
        
        # Save analysis to DB
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE games SET analyzed = 1, analysis_json = ? WHERE id = ?",
                (json.dumps(analysis), game_id)
            )
        
        return analysis
    
    def _find_critical_moments(self, mistakes: List[Dict]) -> List[Dict]:
        # Implement logic to find game phases with most mistakes
        pass
    
    def get_player_stats(self, username: str) -> Dict[str, Any]:
        # Implement player statistics aggregation
        pass

analyzer = ChessAnalyzer()

@app.route('/api/players', methods=['GET'])
def get_players():
    try:
        with sqlite3.connect(analyzer.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all unique white and black players
            cursor.execute("SELECT white FROM games UNION SELECT black FROM games")
            players = [row[0] for row in cursor.fetchall() if row[0]]
            
            return jsonify({
                "status": "success",
                "players": players,
                "count": len(players)
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    game_id = data.get('game_id')
    depth = data.get('depth', 18)
    return jsonify(analyzer.analyze_game(game_id, depth))

@app.route('/import', methods=['POST'])
def import_game():
    pgn_text = request.data.decode('utf-8')
    return jsonify(analyzer.import_pgn(pgn_text))

if __name__ == '__main__':
    app.run(debug=True)