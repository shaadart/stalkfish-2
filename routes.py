from flask import Blueprint, request, jsonify, render_template
from analyzer import analyze_pgn

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/analyze", methods=["POST"])
def analyze_route():
    pgn_text = request.form.get("pgn", "")
    try:
        analysis = analyze_pgn(pgn_text)
        return jsonify(analysis)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
