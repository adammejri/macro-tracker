from flask import Blueprint, jsonify, request
from core.nutrition_service import find_foods, list_all_foods

nutrition_bp = Blueprint("nutrition", __name__)

@nutrition_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    results = find_foods(query)
    return jsonify([dict(row) for row in results])

@nutrition_bp.route("/foods", methods=["GET"])
def get_all_foods():
    foods = list_all_foods()
    return jsonify([dict(row) for row in foods])