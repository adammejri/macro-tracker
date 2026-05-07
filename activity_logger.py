from db import get_logs_db
from datetime import date as today_date
import state

class BackToMainMenu(Exception):
    pass

def check_back(value):
    stripped = value.strip().lower()
    if stripped == "back":
        raise BackToMainMenu
    if state.check_global(stripped):
        return ""
    return value

# ─── TDEE MODEL ───────────────────────────────────────────────────────────────

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

    with get_logs_db() as conn:
        for act in activities:
            row = conn.execute(
                "SELECT * FROM activity_types WHERE name = ?",
                (act["type"],)
            ).fetchone()

            if not row:
                print(f"Unknown activity '{act['type']}', skipping.")
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
        "tef": round(final_tdee * 0.091)
    }

# ─── MACRO TARGETS ────────────────────────────────────────────────────────────

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

# ─── DATABASE HELPERS ─────────────────────────────────────────────────────────

def get_last_weight():
    with get_logs_db() as conn:
        row = conn.execute(
            "SELECT weight FROM daily_info ORDER BY date DESC LIMIT 1"
        ).fetchone()
        return row["weight"] if row else None

def get_last_height_age_gender():
    with get_logs_db() as conn:
        row = conn.execute(
            "SELECT height, age, gender FROM daily_info ORDER BY date DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

def save_daily_info(date, weight, steps, tdee_result, targets, height, age, gender):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT INTO daily_info (date, weight, steps, tdee, bmr, protein_target, carbs_target, fat_target, calorie_target, height, age, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                weight=excluded.weight,
                steps=excluded.steps,
                tdee=excluded.tdee,
                bmr=excluded.bmr,
                protein_target=excluded.protein_target,
                carbs_target=excluded.carbs_target,
                fat_target=excluded.fat_target,
                calorie_target=excluded.calorie_target,
                height=excluded.height,
                age=excluded.age,
                gender=excluded.gender
        """, (
            date,
            weight,
            steps,
            tdee_result["tdee"],
            tdee_result["bmr"],
            targets["protein_target"],
            targets["carbs_target"],
            targets["fat_target"],
            targets["calorie_target"],
            height,
            age,
            gender
        ))

def save_activity(date, activity_type, duration, distance, calories_burned):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT INTO activity_logs (date, activity_type, duration_minutes, distance_km, calories_burned)
            VALUES (?, ?, ?, ?, ?)
        """, (date, activity_type, duration, distance, calories_burned))

def get_activities(date):
    with get_logs_db() as conn:
        return conn.execute(
            "SELECT * FROM activity_logs WHERE date = ?", (date,)
        ).fetchall()

def delete_activity(activity_id):
    with get_logs_db() as conn:
        conn.execute("DELETE FROM activity_logs WHERE id = ?", (activity_id,))

def get_available_activity_types():
    with get_logs_db() as conn:
        return conn.execute("SELECT * FROM activity_types").fetchall()

def add_activity_type(name, metric, met_value=None, kcal_per_kg_per_km=None):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO activity_types (name, metric, met_value, kcal_per_kg_per_km)
            VALUES (?, ?, ?, ?)
        """, (name, metric, met_value, kcal_per_kg_per_km))

# ─── UI ───────────────────────────────────────────────────────────────────────

def prompt_daily_setup(default_weight, default_profile):
    print("\n--- Daily Setup --- (type 'back' at any point to return to main menu)")

    weight_input = check_back(input(f"Weight (kg) [{default_weight}]: "))
    weight = float(weight_input) if weight_input else default_weight

    if default_profile:
        height = default_profile["height"]
        age = default_profile["age"]
        gender = default_profile["gender"]
        print(f"Using last profile: height={height}, age={age}, gender={gender}")
    else:
        height = float(check_back(input("Height (cm): ")))
        age = int(check_back(input("Age: ")))
        gender = check_back(input("Gender (male/female): ")).strip().lower()

    steps_input = check_back(input("Steps today [5000]: "))
    steps = int(steps_input) if steps_input else 5000

    return weight, height, age, gender, steps

def prompt_activities():
    activities = []
    available = get_available_activity_types()

    print("\nAvailable activity types: (type 'back' at any point to return to main menu)")
    for i, row in enumerate(available, 1):
        if row["metric"] == "distance":
            print(f"  {i}. {row['name']} (distance in km)")
        else:
            print(f"  {i}. {row['name']} (duration in minutes)")
    print("  Type 'new' to add a new activity type or 'done' to finish.")

    while True:
        choice = check_back(input("\nActivity (number or 'new' or 'done'): ")).strip().lower()

        if choice == "done":
            break

        elif choice == "new":
            name = check_back(input("Activity name: ")).strip().lower()
            metric = check_back(input("Metric (duration/distance): ")).strip().lower()
            if metric == "duration":
                met = float(check_back(input("MET value: ")))
                add_activity_type(name, metric, met_value=met)
            else:
                kcal = float(check_back(input("kcal per kg per km: ")))
                add_activity_type(name, metric, kcal_per_kg_per_km=kcal)
            print(f"Added '{name}' to activity types.")
            available = get_available_activity_types()

        elif choice.isdigit() and 1 <= int(choice) <= len(available):
            row = available[int(choice) - 1]
            if row["metric"] == "distance":
                dist = float(check_back(input(f"  Distance (km) for {row['name']}: ")))
                activities.append({"type": row["name"], "distance": dist})
            else:
                dur = float(check_back(input(f"  Duration (minutes) for {row['name']}: ")))
                activities.append({"type": row["name"], "duration": dur})
        else:
            print("Invalid choice.")

    return activities

def run_activity_logger(date=None, weight=None, height=None, age=None, gender=None):
    state.push("Activity Logger")
    if date is None:
        date = str(today_date.today())

    default_weight = get_last_weight() or weight
    default_profile = get_last_height_age_gender()

    try:
        weight, height, age, gender, steps = prompt_daily_setup(default_weight, default_profile)
        activities = prompt_activities()
    except BackToMainMenu:
        print("Returning to main menu.")
        state.pop()
        return

    tdee_result = calculate_tdee(weight, height, age, gender, steps, activities)
    targets = calculate_targets(weight, tdee_result["tdee"])

    save_daily_info(date, weight, steps, tdee_result, targets, height, age, gender)

    for act in activities:
        a_type = act["type"]
        duration = act.get("duration", None)
        distance = act.get("distance", None)

        with get_logs_db() as conn:
            row = conn.execute(
                "SELECT * FROM activity_types WHERE name = ?", (a_type,)
            ).fetchone()

        if row["metric"] == "distance":
            burned = weight * distance * row["kcal_per_kg_per_km"]
        else:
            burned = (row["met_value"] * 3.5 * weight / 200) * duration

        save_activity(date, a_type, duration, distance, round(burned, 1))

    print(f"\n--- TDEE Summary for {date} ---")
    print(f"TDEE:     {tdee_result['tdee']} kcal")
    print(f"BMR:      {tdee_result['bmr']} kcal")
    print(f"Exercise: {tdee_result['exercise_net']} kcal")
    print(f"Steps:    {tdee_result['step_burn']} kcal")
    print(f"TEF:      {tdee_result['tef']} kcal")
    print(f"\n--- Macro Targets ---")
    print(f"Calories: {targets['calorie_target']} kcal")
    print(f"Protein:  {targets['protein_target']}g")
    print(f"Carbs:    {targets['carbs_target']}g")
    print(f"Fat:      {targets['fat_target']}g")

    state.pop()
    return weight, height, age, gender, targets