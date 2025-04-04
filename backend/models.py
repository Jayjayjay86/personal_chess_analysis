# models.py
import sqlite3
from typing import List, Dict, Any
import json

class GameModel:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_game(self, game_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM games WHERE id = ?", (game_id,)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
            
        return {
            "id": row[0],
            "pgn": row[1],
            "white": row[2],
            "black": row[3],
            "date": row[4],
            "result": row[5],
            "analyzed": bool(row[6]),
            "analysis": json.loads(row[7]) if row[7] else None
        }
    
    def get_all_games(self, username: str = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM games"
        params = ()
        
        if username:
            query += " WHERE white = ? OR black = ?"
            params = (username, username)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        return [{
            "id": row[0],
            "white": row[2],
            "black": row[3],
            "date": row[4],
            "result": row[5],
            "analyzed": bool(row[6])
        } for row in rows]

class MistakeModel:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_mistakes_by_game(self, game_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM mistakes WHERE game_id = ? ORDER BY move_number", (game_id,)
            )
            rows = cursor.fetchall()
        
        return [{
            "id": row[0],
            "game_id": row[1],
            "move_number": row[2],
            "fen_before": row[3],
            "fen_after": row[4],
            "player_color": row[5],
            "eval_before": row[6],
            "eval_after": row[7],
            "eval_diff": row[8],
            "mistake_type": row[9],
            "clock_time": row[10]
        } for row in rows]
    
    def get_mistakes_by_player(self, username: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT m.* FROM mistakes m
                JOIN games g ON m.game_id = g.id
                WHERE g.white = ? OR g.black = ?
                ORDER BY g.date DESC
            """, (username, username))
            rows = cursor.fetchall()
        
        return [{
            "id": row[0],
            "game_id": row[1],
            "move_number": row[2],
            "fen_before": row[3],
            "fen_after": row[4],
            "player_color": row[5],
            "eval_before": row[6],
            "eval_after": row[7],
            "eval_diff": row[8],
            "mistake_type": row[9],
            "clock_time": row[10]
        } for row in rows]