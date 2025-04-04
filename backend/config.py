import os
from pathlib import Path
from typing import Optional

class Config:
    def __init__(self):
        # Base directories (Windows paths)
        self.DATA_DIR = Path(os.getenv("CHESS_DATA_DIR", "C:/chess_data"))
        self.ANALYSIS_DIR = self.DATA_DIR / "analysis"
        self.PGN_DIR = self.DATA_DIR / "pgn"
        
        # Stockfish configuration (Windows)
        self.ENGINE_PATH = os.getenv("STOCKFISH_PATH", "C:/stockfish/stockfish-windows-x86-64-avx2.exe")
        
        # Engine parameters
        self.ENGINE_DEPTH = int(os.getenv("ANALYSIS_DEPTH", 18))
        self.ENGINE_THREADS = int(os.getenv("ENGINE_THREADS", 2))
        self.ENGINE_HASH = int(os.getenv("ENGINE_HASH", 256))  # MB
        
        # Database configuration
        self.DATABASE_URL = f"sqlite:///{self.DATA_DIR}/chess_games.db"
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Ensure all required directories exist"""
        self.DATA_DIR.mkdir(exist_ok=True, parents=True)
        self.ANALYSIS_DIR.mkdir(exist_ok=True)
        self.PGN_DIR.mkdir(exist_ok=True)
    
    def get_engine_config(self) -> dict:
        return {
            "depth": self.ENGINE_DEPTH,
            "threads": self.ENGINE_THREADS,
            "hash": self.ENGINE_HASH
        }
    
    def verify_stockfish(self) -> bool:
        """Check if Stockfish is accessible"""
        return os.path.exists(self.ENGINE_PATH)

# Singleton configuration instance
config = Config()

if __name__ == "__main__":
    # Test configuration
    print("Configuration Test:")
    print(f"Data Directory: {config.DATA_DIR}")
    print(f"Stockfish Path: {config.ENGINE_PATH}")
    print(f"Stockfish Accessible: {config.verify_stockfish()}")
    print(f"Engine Config: {config.get_engine_config()}")