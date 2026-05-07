from db.activity_repo import get_activity_type

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161

def get_net_burn(bmr, gross_burn, duration_minutes):
    bmr_per_min = bmr / (24 * 60)
    return max(0, gross_burn - (bmr_per_min * duration_minutes))

def calculate_tdee(weight, height, age, gender, steps, activities):
    bmr = calculate_bmr(weight, height, age, gender)
    step_burn = steps * weight * 0.00045

    exercise_gross_burn = 0
    total_exercise_minutes = 0
    skipped = []

    for act in activities:
        row = get_activity_type(act["type"])

        if not row:
            skipped.append(act["type"])
            continue

        if row["metric"] == "distance":
            dist = act.get("distance", 0)
            burn = weight * dist * row["kcal_per_kg_per_km"]
            exercise_gross_burn += burn
            total_exercise_minutes += dist * 5.16
        else:
            duration = act.get("duration", 0)
            burn = (row["met_value"] * 3.5 * weight / 200) * duration
            exercise_gross_burn += burn
            total_exercise_minutes += duration

    exercise_net_burn = get_net_burn(bmr, exercise_gross_burn, total_exercise_minutes)
    total_before_tef = bmr + step_burn + exercise_net_burn
    final_tdee = total_before_tef * 1.1

    return {
        "tdee": round(final_tdee),
        "bmr": round(bmr),
        "exercise_net": round(exercise_net_burn),
        "step_burn": round(step_burn),
        "tef": round(final_tdee * 0.091),
        "skipped": skipped
    }

def calculate_targets(weight, tdee):
    protein_g = round(2.3 * weight, 1)
    protein_kcal = protein_g * 4
    remaining = tdee - protein_kcal
    fat_g = round((remaining * 0.30) / 9, 1)
    carbs_g = round((remaining * 0.40) / 4, 1)
    return {
        "calorie_target": tdee,
        "protein_target": protein_g,
        "fat_target": fat_g,
        "carbs_target": carbs_g
    }