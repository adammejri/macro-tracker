from db.activity_repo import (
    upsert_daily_info,
    insert_activity,
    get_activities_for_date,
    delete_activity,
    get_all_activity_types,
    get_activity_type,
    insert_activity_type,
    get_last_daily_info
)
from core.tdee_service import calculate_tdee, calculate_targets

def get_defaults():
    row = get_last_daily_info()
    if not row:
        return None
    return {
        "weight": row["weight"],
        "height": row["height"],
        "age":    row["age"],
        "gender": row["gender"]
    }

def log_day(date, weight, height, age, gender, steps, activities):
    tdee_result = calculate_tdee(weight, height, age, gender, steps, activities)
    targets = calculate_targets(weight, tdee_result["tdee"])

    upsert_daily_info(
        date, weight, height, age, gender, steps,
        tdee_result["tdee"], tdee_result["bmr"],
        targets["protein_target"], targets["carbs_target"],
        targets["fat_target"], targets["calorie_target"]
    )

    for act in activities:
        a_type = act["type"]
        duration = act.get("duration", None)
        distance = act.get("distance", None)

        row = get_activity_type(a_type)
        if not row:
            continue

        if row["metric"] == "distance":
            burned = weight * distance * row["kcal_per_kg_per_km"]
        else:
            burned = (row["met_value"] * 3.5 * weight / 200) * duration

        insert_activity(date, a_type, duration, distance, round(burned, 1))

    return tdee_result, targets

def get_activities(date):
    return get_activities_for_date(date)

def remove_activity(activity_id):
    delete_activity(activity_id)

def list_activity_types():
    return get_all_activity_types()

def add_activity_type(name, metric, met_value=None, kcal_per_kg_per_km=None):
    insert_activity_type(name, metric, met_value, kcal_per_kg_per_km)