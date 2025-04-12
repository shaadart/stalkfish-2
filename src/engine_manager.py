import os
import chess.engine
from src.config import ENGINE_PATH

class EngineManager:
    def __init__(self):
        if not os.path.exists(ENGINE_PATH):
            raise FileNotFoundError(f"Stockfish not found at {ENGINE_PATH!r}")
        self.engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    def analyze(self, board, depth):
        return self.engine.analyse(board, chess.engine.Limit(depth=depth))

    def close(self):
        self.engine.quit()
