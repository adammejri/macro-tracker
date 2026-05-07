from core.activity_service import (
    log_day, get_activities, remove_activity,
    list_activity_types, add_activity_type, get_defaults
)
import cli.state as state

COMMANDS = {
    "1. Update physical metrics": "Update weight, height, age, gender, steps",
    "2. Add exercise":            "Log an activity for today",
    "3. Delete exercise":         "Remove a logged activity",
    "4. View TDEE summary":       "Show TDEE and macro targets",
    "5. Exit":                    "Return to main menu",
    "where":                      "Show current location",
    "commands":                   "Show this menu"
}

def print_commands():
    print("\nAvailable commands:")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd:<35} {desc}")

class BackToMain(Exception):
    pass

def check_input(value):
    stripped = value.strip().lower()
    if stripped == "back to main":
        raise BackToMain
    result = state.check_global(stripped)
    if result == "commands":
        print_commands()
        return ""
    elif result:
        return ""
    return value

def prompt_physical_metrics(defaults):
    print("\n--- Physical Metrics --- (type 'back to main' to return)")

    val = check_input(input(f"Weight (kg) [{defaults.get('weight', '')}]: "))
    weight = float(val) if val.strip() else defaults.get("weight")

    val = check_input(input(f"Height (cm) [{defaults.get('height', '')}]: "))
    height = float(val) if val.strip() else defaults.get("height")

    val = check_input(input(f"Age [{defaults.get('age', '')}]: "))
    age = int(val) if val.strip() else defaults.get("age")

    val = check_input(input(f"Gender (male/female) [{defaults.get('gender', '')}]: "))
    gender = val.strip().lower() if val.strip() else defaults.get("gender")

    val = check_input(input("Steps today [5000]: "))
    steps = int(val) if val.strip() else 5000

    return weight, height, age, gender, steps

def prompt_add_exercise():
    activities = []
    available = list_activity_types()

    print("\n--- Add Exercise --- (type 'done' when finished, 'back to main' to cancel)")
    print("\nAvailable activity types:")
    for i, row in enumerate(available, 1):
        metric = "distance in km" if row["metric"] == "distance" else "duration in minutes"
        print(f"  {i}. {row['name']} ({metric})")
    print("  new — Add a new activity type")

    while True:
        val = check_input(input("\nActivity (number, 'new', or 'done'): "))
        if not val:
            continue

        choice = val.strip().lower()

        if choice == "done":
            break

        elif choice == "new":
            name = check_input(input("Activity name: ")).strip().lower()
            metric = check_input(input("Metric (duration/distance): ")).strip().lower()
            if metric == "duration":
                met = float(check_input(input("MET value: ")))
                add_activity_type(name, metric, met_value=met)
            else:
                kcal = float(check_input(input("kcal per kg per km: ")))
                add_activity_type(name, metric, kcal_per_kg_per_km=kcal)
            print(f"Added '{name}'.")
            available = list_activity_types()

        elif choice.isdigit() and 1 <= int(choice) <= len(available):
            row = available[int(choice) - 1]
            if row["metric"] == "distance":
                dist = float(check_input(input(f"Distance (km) for {row['name']}: ")))
                activities.append({"type": row["name"], "distance": dist})
            else:
                dur = float(check_input(input(f"Duration (minutes) for {row['name']}: ")))
                activities.append({"type": row["name"], "duration": dur})
            print(f"Added {row['name']}.")
        else:
            print("Invalid choice.")

    return activities

def prompt_delete_exercise(date):
    activities = get_activities(date)
    if not activities:
        print("No activities logged today.")
        return

    print("\nLogged activities:")
    for i, act in enumerate(activities, 1):
        if act["distance_km"]:
            print(f"  {i}. {act['activity_type']}: {act['distance_km']} km — {act['calories_burned']} kcal")
        else:
            print(f"  {i}. {act['activity_type']}: {act['duration_minutes']} min — {act['calories_burned']} kcal")

    choice = input("Type number to delete or 'exit' to cancel: ").strip().lower()
    if choice == "exit":
        print("Cancelled.")
    elif choice.isdigit() and 1 <= int(choice) <= len(activities):
        remove_activity(activities[int(choice) - 1]["id"])
        print("Activity deleted.")
    else:
        print("Invalid choice.")

def print_tdee_summary(tdee_result, targets):
    print(f"\n--- TDEE Summary ---")
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

def run_activity_cli(date):
    print(f"\n--- Activity Logger ({date}) ---")
    print("Type 'commands' to see available options.")

    defaults = get_defaults() or {}
    last_tdee = None
    last_targets = None
    activities = []

    try:
        while True:
            print(f"\n[{state.where()}]")
            print("1. Update physical metrics")
            print("2. Add exercise")
            print("3. Delete exercise")
            print("4. View TDEE summary")
            print("5. Exit")

            val = check_input(input("\n> ").strip())
            if not val:
                continue

            choice = val.strip()

            if choice == "1":
                state.push("Physical Metrics")
                weight, height, age, gender, steps = prompt_physical_metrics(defaults)
                defaults = {"weight": weight, "height": height,
                           "age": age, "gender": gender}
                last_tdee, last_targets = log_day(
                    date, weight, height, age, gender, steps, activities
                )
                print("Physical metrics updated.")
                state.pop()

            elif choice == "2":
                state.push("Add Exercise")
                new_activities = prompt_add_exercise()
                activities.extend(new_activities)
                if defaults and last_tdee:
                    last_tdee, last_targets = log_day(
                        date,
                        defaults["weight"], defaults["height"],
                        defaults["age"], defaults["gender"],
                        defaults.get("steps", 5000), activities
                    )
                state.pop()

            elif choice == "3":
                state.push("Delete Exercise")
                prompt_delete_exercise(date)
                state.pop()

            elif choice == "4":
                if last_tdee and last_targets:
                    print_tdee_summary(last_tdee, last_targets)
                else:
                    print("No TDEE calculated yet. Update physical metrics first.")

            elif choice == "5":
                print("Returning to main menu.")
                break

            else:
                print("Invalid choice. Pick 1-5 or type 'commands'.")

    except BackToMain:
        print("Returning to main menu.")