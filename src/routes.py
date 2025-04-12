from flask import Blueprint, request, jsonify, render_template
from src.analyzer import analyze_pgn
import traceback

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/analyze", methods=["POST"])
def analyze_route():
    pgn = request.form.get("pgn", "")
    try:
        data = analyze_pgn(pgn)
        return jsonify(data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
