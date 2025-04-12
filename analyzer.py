import chess.pgn, io
from engine_manager import EngineManager
from config import ENGINE_DEPTH

def analyze_pgn(pgn_text):
    """
    Parses PGN, runs Stockfish before/after each move,
    and returns a list of dicts with san, eval, tag, from, to.
    """
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Could not parse PGN")

    board = game.board()
    engine_mgr = EngineManager()
    analysis = []

    for move in game.mainline_moves():
        info_before = engine_mgr.analyze(board, ENGINE_DEPTH)
        score_before = info_before['score'].white().score(mate_score=10000)

        san      = board.san(move)
        uci_from = chess.square_name(move.from_square)
        uci_to   = chess.square_name(move.to_square)

        board.push(move)

        info_after = engine_mgr.analyze(board, ENGINE_DEPTH)
        score_after = info_after['score'].white().score(mate_score=10000)

        # classify
        if score_before is None or score_after is None:
            tag = "Unknown"
        else:
            diff = score_after - score_before
            if abs(diff) < 20:
                tag = "Best Move"
            elif abs(diff) < 100:
                tag = "Inaccuracy"
            elif abs(diff) < 300:
                tag = "Mistake"
            else:
                tag = "Blunder"

        analysis.append({
            "san":  san,
            "eval": score_after,
            "tag":  tag,
            "from": uci_from,
            "to":   uci_to
        })

    engine_mgr.close()
    return analysis
