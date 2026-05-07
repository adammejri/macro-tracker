from flask import Blueprint, jsonify
from core.summary_service import get_full_day_summary, get_all_dates, date_has_data

summary_bp = Blueprint("summary", __name__)

@summary_bp.route("/<date>", methods=["GET"])
def get_summary(date):
    if not date_has_data(date):
        return jsonify({"error": f"No data found for {date}"}), 404
    summary = get_full_day_summary(date)
    return jsonify(summary)

@summary_bp.route("/dates", methods=["GET"])
def get_all_logged_dates():
    dates = get_all_dates()
    return jsonify([row["date"] for row in dates])