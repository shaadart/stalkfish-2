import io
import os
import logging

import chess
import chess.pgn
import chess.polyglot
from chess.engine import Limit

from src.engine_manager import EngineManager
from src.config import ENGINE_DEPTH, ENGINE_TIME_MS

# Updated centipawn loss thresholds
CP_THRESHOLDS = [
    ("Best", 0, 20),
    ("Excellent", 20, 50),
    ("Good", 50, 100),
    ("Inaccuracy", 100, 200),
    ("Mistake", 200, 300),
    ("Blunder", 300, float('inf')),
]

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}

BOOK_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "book.bin")
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s - %(message)s'
)

def cp_to_ep(cp: int) -> float:
    """Convert centipawns to expected points without Elo adjustment."""
    x = (cp or 0) / 100
    return 1 / (1 + 10 ** (-x))

def classify_cp_lost(cp_lost: float) -> str:
    """Classify move based on centipawn loss."""
    for tag, lo, hi in CP_THRESHOLDS:
        if lo <= cp_lost < hi:
            return tag
    return "Unknown"

def analyze_pgn(pgn_text: str):
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Could not parse PGN")

    board = game.board()
    engine = EngineManager()

    book = None
    if os.path.exists(BOOK_PATH):
        book = chess.polyglot.open_reader(BOOK_PATH)
        logging.info("Opening book loaded")

    result = []
    last_tag = None

    for move in game.mainline_moves():
        # 1. BEFORE MOVE ANALYSIS
        infos = engine.analyze(
            board,
            Limit(depth=ENGINE_DEPTH, time=ENGINE_TIME_MS),
            multipv=2
        )
        best_info = infos[0]
        cp_b = best_info["score"].white().score(mate_score=10000)
        ep_b = cp_to_ep(cp_b)
        rec_move = best_info.get("pv", [None])[0]
        rec_san = board.san(rec_move) if rec_move else None

        san = board.san(move)
        uci_from = chess.square_name(move.from_square)
        uci_to = chess.square_name(move.to_square)

        in_book = False
        if book:
            try:
                entry = book.find(board)
                in_book = (entry.move == move)
            except:
                pass

        mat_before = sum(
            len(board.pieces(pt, board.turn)) * v
            for pt, v in PIECE_VALUES.items()
        )

        board.push(move)

        # 2. AFTER MOVE ANALYSIS
        info_a = engine.analyze(
            board,
            Limit(depth=ENGINE_DEPTH, time=ENGINE_TIME_MS),
            multipv=1
        )

        if isinstance(info_a, list):
            if len(info_a) == 0:
                raise ValueError("Empty analysis results")
            best_info_a = info_a[0]
            cp_a = best_info_a["score"].white().score(mate_score=10000)
        elif isinstance(info_a, dict):
            cp_a = info_a["score"].white().score(mate_score=10000)
        else:
            raise ValueError("Unexpected analysis format")

        ep_a = cp_to_ep(cp_a)
        cp_lost = max(0.0, (cp_b - cp_a) / 100)  # Convert to pawn units

        mat_after = sum(
            len(board.pieces(pt, not board.turn)) * v
            for pt, v in PIECE_VALUES.items()
        )

        base_tag = classify_cp_lost(cp_lost * 100)  # Convert back to centipawns

        # Determine special tags
        tag = base_tag
        if in_book:
            tag = "Book"
        elif rec_san == san:
            if mat_after < mat_before and ep_a >= ep_b:
                tag = "Brilliant"
            elif cp_lost * 100 <= 20:
                tag = "Best"
            elif cp_lost * 100 <= 50:
                tag = "Excellent"
            else:
                tag = "Good"
        elif ep_b < 0.5 and ep_a >= 0.5:
            tag = "Great"
        elif last_tag in ("Mistake", "Blunder") and base_tag not in ("Best", "Excellent", "Good"):
            tag = "Miss"

        result.append({
            "san": san,
            "from": uci_from,
            "to": uci_to,
            "cp_before": round(cp_b/100, 1),  # In pawn units
            "cp_after": round(cp_a/100, 1),
            "cp_lost": round(cp_lost, 1),
            "ep_before": round(ep_b, 3),
            "ep_after": round(ep_a, 3),
            "recommended": rec_san,
            "tag": tag
        })

        last_tag = tag

    for move_data in result:
        logging.debug(
            f"Move: {move_data['san']}, From: {move_data['from']}, To: {move_data['to']}, "
            f"CP Before: {move_data['cp_before']}, CP After: {move_data['cp_after']}, "
            f"CP Lost: {move_data['cp_lost']}, EP Before: {move_data['ep_before']}, "
            f"EP After: {move_data['ep_after']}, Recommended: {move_data['recommended']}, "
            f"Tag: {move_data['tag']}"
        )

    if book:
        book.close()
    engine.close()

    return result
