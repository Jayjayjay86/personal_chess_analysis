# advanced_analysis.py
from collections import defaultdict
from typing import List, Dict, Tuple
import chess
import chess.pgn
import numpy as np
from scipy import stats

class TimePressureAnalyzer:
    @staticmethod
    def analyze_time_mistakes(mistakes: List[Dict]) -> Dict:
        """Analyze mistakes correlation with remaining time"""
        if not mistakes:
            return {}
            
        time_bins = [0, 30, 60, 120, 300, float('inf')]
        bin_labels = ["<30s", "30-60s", "1-2m", "2-5m", "5m+"]
        mistake_counts = [0] * (len(time_bins) - 1)
        total_moves = [0] * (len(time_bins) - 1)
        
        for mistake in mistakes:
            if mistake['clock_time'] is None:
                continue
                
            for i in range(len(time_bins) - 1):
                if time_bins[i] <= mistake['clock_time'] < time_bins[i + 1]:
                    mistake_counts[i] += 1
                    break
        
        # Calculate mistake rates per time bin
        mistake_rates = []
        for i in range(len(mistake_counts)):
            if total_moves[i] > 0:
                rate = (mistake_counts[i] / total_moves[i]) * 100
            else:
                rate = 0
            mistake_rates.append(rate)
        
        return {
            "time_bins": bin_labels,
            "mistake_counts": mistake_counts,
            "mistake_rates": mistake_rates
        }

class OpeningAnalyzer:
    def __init__(self):
        self.opening_db = {
            "Sicilian Defense": ["e4 c5"],
            "Ruy Lopez": ["e4 e5 Nf3 Nc6 Bb5"],
            "Queen's Gambit": ["d4 d5 c4"],
            # Add more openings as needed
        }
    
    def classify_opening(self, moves: List[str]) -> str:
        """Classify the opening based on move sequence"""
        move_str = " ".join(moves)
        for opening, patterns in self.opening_db.items():
            for pattern in patterns:
                if move_str.startswith(pattern):
                    return opening
        return "Unknown Opening"
    
    def analyze_opening_mistakes(self, games: List[Dict]) -> Dict:
        """Analyze mistakes by opening"""
        opening_stats = defaultdict(lambda: {
            "count": 0,
            "mistakes": 0,
            "avg_rating_diff": 0
        })
        
        for game in games:
            pgn = game['pgn']
            game_obj = chess.pgn.read_game(pgn)
            
            # Get first 10 moves
            moves = []
            board = game_obj.board()
            for node in game_obj.mainline():
                moves.append(board.san(node.move))
                board.push(node.move)
                if len(moves) >= 10:
                    break
            
            opening = self.classify_opening(moves)
            stats = opening_stats[opening]
            stats["count"] += 1
            
            if game['analysis']:
                stats["mistakes"] += len(game['analysis']['mistakes'])
        
        # Calculate averages
        for opening, data in opening_stats.items():
            if data["count"] > 0:
                data["avg_mistakes"] = data["mistakes"] / data["count"]
        
        return dict(opening_stats)

class RatingTrendAnalyzer:
    @staticmethod
    def calculate_rating_trend(games: List[Dict]) -> Dict:
        """Analyze rating changes over time"""
        if not games:
            return {}
            
        dates = []
        ratings = []
        
        for game in games:
            if 'WhiteElo' in game['headers'] and game['headers']['White'] == username:
                ratings.append(int(game['headers']['WhiteElo']))
                dates.append(game['headers']['Date'])
            elif 'BlackElo' in game['headers'] and game['headers']['Black'] == username:
                ratings.append(int(game['headers']['BlackElo']))
                dates.append(game['headers']['Date'])
        
        # Convert dates to ordinal for trend calculation
        date_ordinals = [datetime.strptime(d, "%Y.%m.%d").toordinal() for d in dates]
        
        if len(ratings) < 2:
            return {}
        
        # Calculate linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            date_ordinals, ratings
        )
        
        return {
            "current_rating": ratings[-1],
            "trend": "up" if slope > 0 else "down",
            "trend_strength": abs(slope),
            "r_squared": r_value**2
        }

class EndgameAnalyzer:
    @staticmethod
    def analyze_endgame_performance(games: List[Dict]) -> Dict:
        """Analyze performance in endgames"""
        endgame_stats = {
            "won": 0,
            "lost": 0,
            "drawn": 0,
            "mistakes": 0,
            "total": 0
        }
        
        for game in games:
            if not game['analysis']:
                continue
                
            pgn = game['pgn']
            game_obj = chess.pgn.read_game(pgn)
            board = game_obj.board()
            
            # Find when endgame started (arbitrarily defined as when both sides have <= 10 points)
            endgame_start = None
            for node in game_obj.mainline():
                board.push(node.move)
                material = EndgameAnalyzer._calculate_material(board)
                if material['white'] <= 10 and material['black'] <= 10:
                    endgame_start = board.fullmove_number
                    break
            
            if endgame_start:
                endgame_stats["total"] += 1
                result = game['headers']['Result']
                
                if result == '1-0' and game['headers']['White'] == username:
                    endgame_stats["won"] += 1
                elif result == '0-1' and game['headers']['Black'] == username:
                    endgame_stats["won"] += 1
                elif result == '1/2-1/2':
                    endgame_stats["drawn"] += 1
                else:
                    endgame_stats["lost"] += 1
                
                # Count endgame mistakes
                for mistake in game['analysis']['mistakes']:
                    if mistake['move_number'] >= endgame_start:
                        endgame_stats["mistakes"] += 1
        
        return endgame_stats
    
    @staticmethod
    def _calculate_material(board: chess.Board) -> Dict[str, int]:
        """Calculate material count for both sides"""
        material = {'white': 0, 'black': 0}
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    material['white'] += value
                else:
                    material['black'] += value
        
        return material