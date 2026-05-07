from flask import Blueprint, jsonify, request
from core.activity_service import (
    log_day, get_activities, remove_activity,
    list_activity_types, add_activity_type, get_defaults
)

activities_bp = Blueprint("activities", __name__)

@activities_bp.route("/types", methods=["GET"])
def get_activity_types():
    types = list_activity_types()
    return jsonify([dict(row) for row in types])

@activities_bp.route("/types", methods=["POST"])
def create_activity_type():
    data = request.get_json()
    name   = data.get("name")
    metric = data.get("metric")
    met    = data.get("met_value")
    kcal   = data.get("kcal_per_kg_per_km")

    if not name or not metric:
        return jsonify({"error": "Missing name or metric"}), 400

    add_activity_type(name, metric, met, kcal)
    return jsonify({"message": f"Activity type '{name}' added"}), 201

@activities_bp.route("/<date>", methods=["GET"])
def get_day_activities(date):
    activities = get_activities(date)
    return jsonify([dict(a) for a in activities])

@activities_bp.route("/<date>", methods=["POST"])
def log_activities(date):
    data       = request.get_json()
    weight     = data.get("weight")
    height     = data.get("height")
    age        = data.get("age")
    gender     = data.get("gender")
    steps      = data.get("steps", 5000)
    activities = data.get("activities", [])

    if not all([weight, height, age, gender]):
        defaults = get_defaults()
        if not defaults:
            return jsonify({"error": "Missing physical metrics and no previous data found"}), 400
        weight = weight or defaults["weight"]
        height = height or defaults["height"]
        age    = age    or defaults["age"]
        gender = gender or defaults["gender"]

    tdee_result, targets = log_day(date, weight, height, age, gender, steps, activities)
    return jsonify({
        "tdee":    tdee_result,
        "targets": targets
    }), 201

@activities_bp.route("/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    remove_activity(activity_id)
    return jsonify({"message": "Activity deleted"}), 200