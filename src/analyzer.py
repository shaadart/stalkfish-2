import chess.pgn, io
import chess
from src.engine_manager import EngineManager
from src.config import ENGINE_DEPTH
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_pgn(pgn_text):
    logging.info("Starting PGN analysis")
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Could not parse PGN")

    board = game.board()
    mgr   = EngineManager()
    result = []

    for move in game.mainline_moves():
        try:
            info_before = mgr.analyze(board, ENGINE_DEPTH)
            score_before = info_before['score'].white().score(mate_score=10000)

            san      = board.san(move)
            uci_from = chess.square_name(move.from_square)
            uci_to   = chess.square_name(move.to_square)

            board.push(move)

            info_after  = mgr.analyze(board, ENGINE_DEPTH)
            score_after = info_after['score'].white().score(mate_score=10000)

            diff = (score_after or 0) - (score_before or 0)
            if score_before is None or score_after is None:
                tag = "Unknown"
            elif abs(diff) < 20:
                tag = "Best Move"
            elif abs(diff) < 100:
                tag = "Inaccuracy"
            elif abs(diff) < 300:
                tag = "Mistake"
            else:
                tag = "Blunder"

            result.append({
                "san":  san,
                "eval": score_after,
                "tag":  tag,
                "from": uci_from,
                "to":   uci_to
            })
        except Exception as e:
            logging.error(f"Error analyzing move {move}: {e}")
            result.append({
                "san": board.san(move),
                "eval": None,
                "tag": "Error",
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square)
            })

    mgr.close()
    logging.info("PGN analysis completed")
    return result
