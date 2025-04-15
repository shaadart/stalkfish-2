import io, os, logging
import chess, chess.pgn, chess.polyglot
from chess.engine import Limit
from src.engine_manager import EngineManager
from src.config import ENGINE_DEPTH, ENGINE_TIME_MS

# Classification V2 thresholds
EP_THRESHOLDS = [
    ("Best",      0.00, 0.00),
    ("Excellent", 0.00, 0.02),
    ("Good",      0.02, 0.05),
    ("Inaccuracy",0.05, 0.10),
    ("Mistake",   0.10, 0.20),
    ("Blunder",   0.20, 1.00),
]

# Optional opening book
BOOK_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         os.pardir, "book.bin"))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def cp_to_ep(cp: int, rating_diff: float=0) -> float:
    """
    Approximate Chess.com's data‐driven mapping:
    logistic((cp/100) + (rating_diff/400))
    """
    x = (cp or 0)/100 + rating_diff/400
    return 1 / (1 + 10**(-x))

def classify_ep_lost(ep_lost: float):
    for tag, lo, hi in EP_THRESHOLDS:
        if lo <= ep_lost <= hi:
            return tag
    return "Unknown"

def analyze_pgn(pgn_text: str):
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Could not parse PGN")

    # extract ratings from headers (fallback to 1500)
    wr = int(game.headers.get("WhiteElo", 1500))
    br = int(game.headers.get("BlackElo", 1500))

    board = game.board()
    engine = EngineManager()

    # set MultiPV=2 so we get top-2 lines
    engine.configure({"MultiPV": 2})

    # optional polyglot book
    book = None
    if os.path.exists(BOOK_PATH):
        book = chess.polyglot.open_reader(BOOK_PATH)

    result = []
    last_tag = None

    for move in game.mainline_moves():
        # 1) before‐move analysis
        info_list = engine.analyze(board,
            Limit(depth=ENGINE_DEPTH, time=ENGINE_TIME_MS),
            multipv=2
        )
        best_info = info_list[0]
        cp_before = best_info["score"].white().score(mate_score=10000)
        ep_before = cp_to_ep(cp_before,
            (wr-br) if board.turn else (br-wr)
        )

        # recommended = SAN of engine’s #1 move
        rec_move = best_info.get("pv", [None])[0]
        rec_san  = board.san(rec_move) if rec_move else None

        # prepare metadata
        san      = board.san(move)
        uci_from = chess.square_name(move.from_square)
        uci_to   = chess.square_name(move.to_square)
        in_book  = False
        if book:
            try:
                e = book.find(board)
                in_book = (e.move == move)
            except:
                pass

        mat_before = sum(len(board.pieces(pt, board.turn))*val
                         for pt,val in PIECE_VALUES.items())

        board.push(move)

        # 2) after‐move analysis
        info_after = engine.analyze(board,
            Limit(depth=ENGINE_DEPTH, time=ENGINE_TIME_MS)
        )
        cp_after = info_after["score"].white().score(mate_score=10000)
        ep_after = cp_to_ep(cp_after,
            (wr-br) if not board.turn else (br-wr)
        )

        mat_after = sum(len(board.pieces(pt, not board.turn))*val
                        for pt,val in PIECE_VALUES.items())

        ep_lost = max(0, ep_before - ep_after)
        base_tag = classify_ep_lost(ep_lost)

        # 3) special overrides
        tag = base_tag
        if in_book:
            tag = "Book"
        elif (base_tag == "Best" and san == rec_san
              and mat_after < mat_before and ep_after >= ep_before):
            tag = "Brilliant"
        elif ep_before < 0.5 and ep_after >= 0.5:
            tag = "Great"
        elif last_tag in ("Mistake","Blunder") and base_tag != "Best":
            tag = "Miss"

        result.append({
            "san":         san,
            "from":        uci_from,
            "to":          uci_to,
            "ep_before":   round(ep_before,3),
            "ep_after":    round(ep_after,3),
            "ep_lost":     round(ep_lost,3),
            "recommended": rec_san,
            "tag":         tag
        })

        last_tag = tag

    if book: book.close()
    engine.close()
    return result
