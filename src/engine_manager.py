import os
import logging
import chess.engine
from src.config import ENGINE_PATH

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EngineManager:
    def __init__(self):
        if not os.path.exists(ENGINE_PATH):
            raise FileNotFoundError(f"Stockfish not found at {ENGINE_PATH!r}")
        logging.info(f"Starting Stockfish at {ENGINE_PATH}")
        self.engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    def analyze(self, board, limit, multipv: int = 1):
        """
        board:   a chess.Board()
        limit:   a chess.engine.Limit(depth=..., time=...)
        multipv: how many principal variations to return
        Returns:
        - If multipv>1: a list of info‑dicts
        - Else:         a single info‑dict
        """
        try:
            infos = self.engine.analyse(board, limit, multipv=multipv)
            if multipv > 1:
                return infos  # list
            else:
                return infos[0] if isinstance(infos, list) else infos  # single dict
        except Exception as e:
            logging.error(f"Engine analysis error: {e}")
            raise

    def close(self):
        try:
            self.engine.quit()
            logging.info("Stockfish closed")
        except Exception as e:
            logging.error(f"Error closing engine: {e}")
