from flask import Flask, request, jsonify, render_template
import chess.pgn, chess.engine
import io, os, traceback

app = Flask(__name__)
engine_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 1) Ensure engine exists
        if not os.path.exists(engine_path):
            return jsonify({"error": f"Stockfish not found at {engine_path!r}"}), 500

        # 2) Parse PGN
        pgn_text = request.form.get('pgn', '')
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return jsonify({"error": "Could not parse PGN"}), 400

        board = game.board()

        # 3) Launch engine
        try:
            engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        except Exception as fe:
            return jsonify({"error": f"Failed to launch engine: {fe}"}), 500

        analysis = []
        for move in game.mainline_moves():
            # eval before move
            info_before = engine.analyse(board, chess.engine.Limit(depth=15))
            score_before = info_before['score'].white().score(mate_score=10000)

            # get SAN *before* pushing
            san = board.san(move)

            # make the move
            board.push(move)

            # eval after move
            info_after = engine.analyse(board, chess.engine.Limit(depth=15))
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
                'san': san,
                'eval': score_after,
                'tag': tag
            })

        engine.quit()
        return jsonify(analysis)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
