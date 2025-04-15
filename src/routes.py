from flask import Blueprint, request, jsonify, render_template
from src.analyzer import analyze_pgn
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/analyze", methods=["POST"])
def analyze_route():
    pgn = request.form.get("pgn", "")
    logging.debug(f"Received PGN: {pgn}")
    try:
        data = analyze_pgn(pgn)
        return jsonify(data)
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
