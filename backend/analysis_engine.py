# analysis_engine.py
import chess
import chess.engine
import chess.pgn
from typing import List, Dict, Any, Tuple
import statistics
from dataclasses import dataclass
from enum import Enum
import time

class MistakeType(Enum):
    BLUNDER = "blunder"
    MISTAKE = "mistake"
    INACCURACY = "inaccuracy"

@dataclass
class Mistake:
    move_number: int
    player: str
    fen_before: str
    fen_after: str
    eval_before: float
    eval_after: float
    eval_diff: float
    type: MistakeType
    clock_time: float
    move_san: str

class GamePhase(Enum):
    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"

class CriticalityAnalyzer:
    @staticmethod
    def calculate_criticality(mistakes: List[Mistake]) -> List[Dict]:
        """Identify critical phases of the game"""
        if not mistakes:
            return []
            
        move_numbers = [m.move_number for m in mistakes]
        avg = statistics.mean(move_numbers)
        stdev = statistics.stdev(move_numbers) if len(move_numbers) > 1 else 0
        
        critical_moments = []
        window_size = 5
        
        for i in range(len(mistakes) - window_size + 1):
            window = mistakes[i:i+window_size]
            density = len(window) / window_size
            avg_eval_diff = statistics.mean(m.eval_diff for m in window)
            
            if density > 0.6 and avg_eval_diff > 100:
                critical_moments.append({
                    "start_move": window[0].move_number,
                    "end_move": window[-1].move_number,
                    "avg_eval_diff": avg_eval_diff,
                    "mistake_count": len(window)
                })
        
        return critical_moments

class GameAnalyzer:
    def __init__(self, engine_path: str):
        self.engine_path = engine_path
    
    def analyze_game(self, pgn_text: str, depth: int = 18) -> Dict[str, Any]:
        game = chess.pgn.read_game(pgn_text)
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
        
        for node in game.mainline():
            move = node.move
            player = "white" if board.turn == chess.WHITE else "black"
            clock_time = node.clock() if hasattr(node, "clock") else None
            
            # Evaluate position before move
            info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
            eval_before = self._normalize_eval(info_before["score"])
            
            board.push(move)
            
            # Evaluate position after move
            info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
            eval_after = self._normalize_eval(info_after["score"])
            
            eval_diff = abs(eval_after - eval_before)
            mistake = self._classify_mistake(
                move_number=board.fullmove_number,
                player=player,
                fen_before=board.fen(),
                fen_after=board.fen(),
                eval_before=eval_before,
                eval_after=eval_after,
                eval_diff=eval_diff,
                clock_time=clock_time,
                move_san=board.san(move)
            )
            
            if mistake:
                analysis["mistakes"].append(mistake)
                
                if player == "white":
                    analysis["summary"]["white_mistakes"] += 1
                else:
                    analysis["summary"]["black_mistakes"] += 1
        
        engine.quit()
        
        if analysis["mistakes"]:
            analysis["summary"]["worst_mistake"] = max(
                analysis["mistakes"], key=lambda m: m.eval_diff
            )
            analysis["summary"]["critical_moments"] = (
                CriticalityAnalyzer.calculate_criticality(analysis["mistakes"])
            )
        
        return analysis
    
    def _normalize_eval(self, score: chess.engine.PovScore) -> float:
        """Convert score to centipawns from white's perspective"""
        return score.white().score(mate_score=10000)
    
    def _classify_mistake(self, **kwargs) -> Optional[Mistake]:
        eval_diff = kwargs["eval_diff"]
        
        if eval_diff > 200:
            kwargs["type"] = MistakeType.BLUNDER
        elif eval_diff > 100:
            kwargs["type"] = MistakeType.MISTAKE
        elif eval_diff > 50:
            kwargs["type"] = MistakeType.INACCURACY
        else:
            return None
        
        return Mistake(**kwargs)