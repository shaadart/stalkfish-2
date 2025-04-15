import os
import chess.engine
import logging
from src.config import ENGINE_PATH

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class EngineManager:
    def __init__(self):
        if not os.path.exists(ENGINE_PATH):
            raise FileNotFoundError(f"Stockfish not found at {ENGINE_PATH!r}")
        try:
            logging.info(f"Initializing Stockfish engine at {ENGINE_PATH}")
            self.engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
            logging.info("Stockfish engine started successfully.")
        except Exception as e:
            logging.error(f"Failed to start Stockfish engine: {e}")
            raise

    def analyze(self, board, depth):
        try:
            return self.engine.analyse(board, chess.engine.Limit(depth=depth))
        except Exception as e:
            logging.error(f"Error during analysis: {e}")
            raise

    def close(self):
        try:
            self.engine.quit()
            logging.info("Stockfish engine closed successfully.")
        except Exception as e:
            logging.error(f"Error while closing the engine: {e}")
