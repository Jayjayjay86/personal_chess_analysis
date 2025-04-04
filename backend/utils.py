# utils.py
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
import chess.pgn
from datetime import datetime

def generate_game_id(game: chess.pgn.Game) -> str:
    """Generate unique ID for a game"""
    headers = game.headers
    unique_str = f"{headers.get('White','')}-{headers.get('Black','')}-{headers.get('Date','')}-{headers.get('Result','')}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def save_analysis_to_file(game_id: str, analysis: Dict[str, Any], output_dir: str = "./analysis"):
    """Save analysis JSON to file"""
    Path(output_dir).mkdir(exist_ok=True)
    file_path = Path(output_dir) / f"{game_id}.json"
    
    with open(file_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    return file_path

def load_analysis_from_file(game_id: str, input_dir: str = "./analysis") -> Optional[Dict[str, Any]]:
    """Load analysis JSON from file"""
    file_path = Path(input_dir) / f"{game_id}.json"
    
    if not file_path.exists():
        return None
    
    with open(file_path, 'r') as f:
        return json.load(f)

def pgn_to_json(pgn_text: str) -> Dict[str, Any]:
    """Convert PGN to JSON structure"""
    game = chess.pgn.read_game(pgn_text)
    if not game:
        return None
    
    result = {
        "headers": dict(game.headers),
        "moves": []
    }
    
    board = game.board()
    for node in game.mainline():
        move = node.move
        result["moves"].append({
            "move": board.san(move),
            "fen": board.fen(),
            "clock": node.clock() if hasattr(node, "clock") else None
        })
        board.push(move)
    
    return result

def format_timestamp(timestamp: float) -> str:
    """Format timestamp to readable date"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def calculate_time_control(headers: Dict[str, str]) -> Optional[str]:
    """Extract time control from game headers"""
    tc = headers.get("TimeControl")
    if not tc:
        return None
    
    if tc == "-":
        return "Correspondence"
    
    parts = tc.split("+")
    initial = int(parts[0]) // 60  # Convert to minutes
    increment = int(parts[1]) if len(parts) > 1 else 0
    
    if increment > 0:
        return f"{initial}+{increment}"
    return f"{initial} min"

# config.py
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.DATA_DIR = Path(os.getenv("CHESS_DATA_DIR", "./data"))
        self.ANALYSIS_DIR = self.DATA_DIR / "analysis"
        self.PGN_DIR = self.DATA_DIR / "pgn"
        self.ENGINE_PATH = os.getenv("STOCKFISH_PATH", "./stockfish")
        self.ENGINE_DEPTH = int(os.getenv("ANALYSIS_DEPTH", 18))
        self.ENGINE_THREADS = int(os.getenv("ENGINE_THREADS", 2))
        self.ENGINE_HASH = int(os.getenv("ENGINE_HASH", 2048))
        
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.ANALYSIS_DIR.mkdir(exist_ok=True)
        self.PGN_DIR.mkdir(exist_ok=True)
    
    def get_engine_config(self) -> Dict[str, Any]:
        return {
            "depth": self.ENGINE_DEPTH,
            "threads": self.ENGINE_THREADS,
            "hash": self.ENGINE_HASH
        }

config = Config()