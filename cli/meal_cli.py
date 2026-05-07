from core.meal_service import add_food_to_meal, remove_meal, remove_food, get_meal_summary, get_daily_totals
from core.nutrition_service import find_foods
from db.activity_repo import get_targets_for_date, get_meals_for_date
from db.meal_repo import get_foods_in_meal
import cli.state as state

COMMANDS = {
    "meal <name>":              "Create a new meal",
    "switch <name>":            "Switch to an existing meal",
    "search <food>":            "Search for a food",
    "select <number> <grams>":  "Add searched food by number and grams",
    "delete meal":              "Delete an entire meal",
    "delete food":              "Delete a food item from a meal",
    "summary":                  "Show meal summary for the day",
    "done":                     "Finish current input session",
    "exit":                     "Go back one level",
    "back to main":             "Return to main menu",
    "where":                    "Show current location in menu",
    "commands":                 "Show available commands"
}

def print_commands():
    print("\nAvailable commands:")
    for cmd, desc in COMMANDS.items():
        print(f"  {cmd:<30} {desc}")

def print_summary(date):
    meals = get_meal_summary(date)
    targets = get_targets_for_date(date)

    if not meals:
        print("No meals logged yet.")
        return

    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for meal in meals:
        print(f"\n--- {meal['meal_name']} ---")
        for item in meal["foods"]:
            print(f"  {item['food_name']} ({item['brand']}) {item['grams']}g: "
                  f"{item['calories']} kcal | P: {item['protein']}g | "
                  f"C: {item['carbs']}g | F: {item['fat']}g")
        t = meal["totals"]
        print(f"  Meal total: {t['calories']} kcal | P: {t['protein']}g | "
              f"C: {t['carbs']}g | F: {t['fat']}g")
        for key in total:
            total[key] += t[key]

    print(f"\n=== Daily Total ===")
    if targets:
        print(f"Calories: {round(total['calories'],1)} / {targets['calorie_target']} kcal")
        print(f"Protein:  {round(total['protein'],1)} / {targets['protein_target']}g")
        print(f"Carbs:    {round(total['carbs'],1)} / {targets['carbs_target']}g")
        print(f"Fat:      {round(total['fat'],1)} / {targets['fat_target']}g")
    else:
        print(f"Calories: {round(total['calories'],1)} kcal")
        print(f"Protein:  {round(total['protein'],1)}g")
        print(f"Carbs:    {round(total['carbs'],1)}g")
        print(f"Fat:      {round(total['fat'],1)}g")
        print("(No targets set — log activities first to calculate TDEE)")

def run_meal_cli(date):
    meal_name = None
    last_search_results = []

    print(f"\n--- Meal Logger ({date}) ---")
    print("Type 'commands' to see available commands.")

    while True:
        prompt = f"\n[{state.where()}]> "
        command = input(prompt).strip().lower()

        global_result = state.check_global(command)
        if global_result == "commands":
            print_commands()
            continue
        elif global_result:
            continue

        if command == "back to main":
            if meal_name:
                state.pop()
            print("Returning to main menu.")
            break

        elif command == "exit":
            if meal_name:
                state.pop()
                meal_name = None
                last_search_results = []
                print("Returned to meal logger top level.")
            else:
                print("Already at meal logger top level. Use 'back to main' to return to main menu.")

        elif command.startswith("meal "):
            new_meal = command[5:]
            existing = [r["meal_name"] for r in get_meals_for_date(date)]
            if new_meal in existing:
                print(f"Meal '{new_meal}' already exists. Use 'switch {new_meal}'.")
            else:
                if meal_name:
                    state.pop()
                meal_name = new_meal
                state.push(f"meal:{meal_name}")
                print(f"Meal '{meal_name}' created. Now adding to '{meal_name}'.")

        elif command.startswith("switch "):
            target = command[7:]
            existing = [r["meal_name"] for r in get_meals_for_date(date)]
            if target not in existing:
                print(f"No meal named '{target}'. Create it with 'meal {target}'.")
            else:
                if meal_name:
                    state.pop()
                meal_name = target
                state.push(f"meal:{meal_name}")
                print(f"Switched to '{meal_name}'.")

        elif command.startswith("search "):
            query = command[7:]
            results = find_foods(query)
            if not results:
                print(f"No foods found matching '{query}'")
            else:
                last_search_results = results
                for i, row in enumerate(results, 1):
                    print(f"{i}. {row['name']} ({row['brand']}): "
                          f"{row['calories']} kcal | P: {row['protein']}g | "
                          f"C: {row['carbs']}g | F: {row['fat']}g")

        elif command.startswith("select "):
            if not meal_name:
                print("Create a meal first with 'meal <name>'")
                continue
            if not last_search_results:
                print("Search for a food first with 'search <food>'")
                continue

            parts = command[7:].split()
            if len(parts) != 2:
                print("Usage: select <number> <grams>")
                continue

            number, grams = int(parts[0]), float(parts[1])

            if number < 1 or number > len(last_search_results):
                print(f"Pick a number between 1 and {len(last_search_results)}")
                continue

            food_row = last_search_results[number - 1]
            food = add_food_to_meal(date, meal_name, food_row, grams)
            print(f"Added {grams}g of {food['name']} ({food['brand']}): "
                  f"{food['calories']} kcal | P: {food['protein']}g")
            print(f"Still adding to '{meal_name}'. Type 'done' when finished.")

        elif command == "done":
            if meal_name:
                state.pop()
                meal_name = None
                last_search_results = []
                print("Finished adding food. Back at meal logger top level.")
            else:
                print("Nothing in progress. Use 'exit' or 'back to main'.")

        elif command == "delete meal":
            meals = get_meals_for_date(date)
            if not meals:
                print("No meals to delete.")
                continue

            for i, m in enumerate(meals, 1):
                print(f"{i}. {m['meal_name']}")
            print("Type the number to delete or 'exit' to cancel.")

            choice = input("> ").strip().lower()
            if choice == "exit":
                print("Cancelled.")
            elif choice.isdigit() and 1 <= int(choice) <= len(meals):
                deleted = meals[int(choice) - 1]["meal_name"]
                remove_meal(date, deleted)
                if meal_name == deleted:
                    state.pop()
                    meal_name = None
                print(f"Deleted meal '{deleted}'.")
            else:
                print("Invalid choice.")

        elif command == "delete food":
            meals = get_meals_for_date(date)
            if not meals:
                print("No meals exist yet.")
                continue

            for i, m in enumerate(meals, 1):
                print(f"{i}. {m['meal_name']}")
            print("Type the number of the meal or 'exit' to cancel.")

            choice = input("> ").strip().lower()
            if choice == "exit":
                print("Cancelled.")
                continue
            if not choice.isdigit() or not (1 <= int(choice) <= len(meals)):
                print("Invalid choice.")
                continue

            selected_meal = meals[int(choice) - 1]["meal_name"]
            items = get_foods_in_meal(date, selected_meal)

            if not items:
                print(f"No foods in '{selected_meal}'.")
                continue

            for i, item in enumerate(items, 1):
                print(f"{i}. {item['food_name']} ({item['brand']}) {item['grams']}g")
            print("Type the number to delete or 'exit' to cancel.")

            choice2 = input("> ").strip().lower()
            if choice2 == "exit":
                print("Cancelled.")
            elif choice2.isdigit() and 1 <= int(choice2) <= len(items):
                deleted = items[int(choice2) - 1]
                remove_food(deleted["id"])
                print(f"Deleted {deleted['food_name']} from '{selected_meal}'.")
            else:
                print("Invalid choice.")

        elif command == "summary":
            print_summary(date)

        else:
            print("Unknown command. Type 'commands' to see available commands.")