from flask import Blueprint, jsonify, request
from core.meal_service import (
    add_food_to_meal, remove_meal, remove_food,
    get_meal_summary, get_daily_totals
)
from core.nutrition_service import find_foods
from db.meal_repo import get_meals_for_date, get_foods_in_meal

meals_bp = Blueprint("meals", __name__)

@meals_bp.route("/<date>", methods=["GET"])
def get_meals(date):
    summary = get_meal_summary(date)
    totals  = get_daily_totals(date)
    return jsonify({"meals": summary, "totals": totals})

@meals_bp.route("/<date>/<meal_name>", methods=["POST"])
def add_food(date, meal_name):
    data = request.get_json()
    food_id = data.get("food_id")
    grams   = data.get("grams")

    if not food_id or not grams:
        return jsonify({"error": "Missing food_id or grams"}), 400

    from db.connection import get_nutrition_db
    with get_nutrition_db() as conn:
        food_row = conn.execute(
            "SELECT * FROM foods WHERE id = ?", (food_id,)
        ).fetchone()

    if not food_row:
        return jsonify({"error": "Food not found"}), 404

    food = add_food_to_meal(date, meal_name, food_row, grams)
    return jsonify(food), 201

@meals_bp.route("/<date>/<meal_name>", methods=["DELETE"])
def delete_meal(date, meal_name):
    remove_meal(date, meal_name)
    return jsonify({"message": f"Meal '{meal_name}' deleted"}), 200

@meals_bp.route("/food/<int:food_log_id>", methods=["DELETE"])
def delete_food(food_log_id):
    remove_food(food_log_id)
    return jsonify({"message": "Food entry deleted"}), 200