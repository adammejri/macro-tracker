from db import get_nutrition_db, get_logs_db
from datetime import date as today_date
import state

# ─── DATABASE HELPERS ─────────────────────────────────────────────────────────

def search_foods(query):
    with get_nutrition_db() as conn:
        return conn.execute("""
            SELECT id, name, brand, calories, protein, carbs, fat
            FROM foods
            WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ?
        """, (f"%{query}%", f"%{query}%")).fetchall()

def get_meals_for_date(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT DISTINCT meal_name FROM meal_logs WHERE date = ?
        """, (date,)).fetchall()

def get_foods_in_meal(date, meal_name):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT id, food_name, brand, grams, calories, protein, carbs, fat
            FROM meal_logs
            WHERE date = ? AND meal_name = ?
        """, (date, meal_name)).fetchall()

def save_food_to_meal(date, meal_name, food):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT INTO meal_logs (date, meal_name, food_name, brand, grams, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            meal_name,
            food["name"],
            food["brand"],
            food["grams"],
            food["calories"],
            food["protein"],
            food["carbs"],
            food["fat"]
        ))

def delete_meal(date, meal_name):
    with get_logs_db() as conn:
        conn.execute("""
            DELETE FROM meal_logs WHERE date = ? AND meal_name = ?
        """, (date, meal_name))

def delete_food_from_meal(food_id):
    with get_logs_db() as conn:
        conn.execute("DELETE FROM meal_logs WHERE id = ?", (food_id,))

def get_daily_totals(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT
                ROUND(SUM(calories), 1) as total_calories,
                ROUND(SUM(protein), 1)  as total_protein,
                ROUND(SUM(carbs), 1)    as total_carbs,
                ROUND(SUM(fat), 1)      as total_fat
            FROM meal_logs
            WHERE date = ?
        """, (date,)).fetchone()

def get_targets_for_date(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT calorie_target, protein_target, carbs_target, fat_target
            FROM daily_info
            WHERE date = ?
        """, (date,)).fetchone()

# ─── UI HELPERS ───────────────────────────────────────────────────────────────

def print_summary(date):
    meals = get_meals_for_date(date)
    targets = get_targets_for_date(date)

    if not meals:
        print("No meals logged yet.")
        return

    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for meal_row in meals:
        meal_name = meal_row["meal_name"]
        items = get_foods_in_meal(date, meal_name)
        meal_totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        print(f"\n--- {meal_name} ---")
        for item in items:
            print(f"  {item['food_name']} ({item['brand']}) {item['grams']}g: "
                  f"{item['calories']} kcal | P: {item['protein']}g | "
                  f"C: {item['carbs']}g | F: {item['fat']}g")
            meal_totals["calories"] += item["calories"]
            meal_totals["protein"]  += item["protein"]
            meal_totals["carbs"]    += item["carbs"]
            meal_totals["fat"]      += item["fat"]

        print(f"  Meal total: {round(meal_totals['calories'],1)} kcal | "
              f"P: {round(meal_totals['protein'],1)}g | "
              f"C: {round(meal_totals['carbs'],1)}g | "
              f"F: {round(meal_totals['fat'],1)}g")

        for key in total:
            total[key] += meal_totals[key]

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
        print("(No targets set — run activity logger first to calculate TDEE)")

# ─── MAIN UI ──────────────────────────────────────────────────────────────────

def run_meal_logger(date=None):
    if date is None:
        date = str(today_date.today())

    meal_name = None
    last_search_results = []

    print(f"\n--- Meal Logger ({date}) ---")
    print("Commands: 'meal <name>', 'switch <name>', 'search <food>', "
          "'select <number> <grams>', 'delete meal', 'delete food', 'summary', 'where', 'exit', 'back'")

    while True:
        command = input("\n> ").strip().lower()

        if command == "back":
            if meal_name:
                state.pop()
            print("Returning to main menu.")
            break

        elif command == "where":
            print(f"Current location: {state.where()}")

        elif command == "exit":
            if meal_name is None and not last_search_results:
                print("Already at top level.")
            else:
                if meal_name:
                    state.pop()
                meal_name = None
                last_search_results = []
                print("Returned to top level.")

        elif command.startswith("meal "):
            new_meal = command[5:]
            existing = [r["meal_name"] for r in get_meals_for_date(date)]
            if new_meal in existing:
                print(f"Meal '{new_meal}' already exists. Use 'switch {new_meal}' to add food to it.")
            else:
                if meal_name:
                    state.pop()
                meal_name = new_meal
                state.push(f"meal:{meal_name}")
                print(f"Meal '{meal_name}' created. You are now adding to '{meal_name}'.")

        elif command.startswith("switch "):
            target = command[7:]
            existing = [r["meal_name"] for r in get_meals_for_date(date)]
            if target not in existing:
                print(f"No meal named '{target}'. Create it first with 'meal {target}'.")
            else:
                if meal_name:
                    state.pop()
                meal_name = target
                state.push(f"meal:{meal_name}")
                print(f"Switched to '{meal_name}'.")

        elif command.startswith("search "):
            query = command[7:]
            results = search_foods(query)
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
            factor = grams / 100

            food = {
                "name":     food_row["name"],
                "brand":    food_row["brand"],
                "grams":    grams,
                "calories": round(food_row["calories"] * factor, 1),
                "protein":  round(food_row["protein"]  * factor, 1),
                "carbs":    round(food_row["carbs"]    * factor, 1),
                "fat":      round(food_row["fat"]      * factor, 1)
            }

            save_food_to_meal(date, meal_name, food)
            print(f"Added {grams}g of {food['name']} ({food['brand']}): "
                  f"{food['calories']} kcal, {food['protein']}g protein")
            print(f"Still adding to '{meal_name}'. Search for more or type 'exit'.")

        elif command == "delete meal":
            meals = get_meals_for_date(date)
            if not meals:
                print("No meals to delete.")
                continue

            for i, m in enumerate(meals, 1):
                print(f"{i}. {m['meal_name']}")
            print("Type the number to delete or 'exit' to cancel.")

            choice = input("\n> ").strip().lower()
            if choice == "exit":
                print("Cancelled.")
            elif choice.isdigit() and 1 <= int(choice) <= len(meals):
                deleted = meals[int(choice) - 1]["meal_name"]
                delete_meal(date, deleted)
                if meal_name == deleted:
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

            choice = input("\n> ").strip().lower()
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
            print("Type the number of the food to delete or 'exit' to cancel.")

            choice2 = input("\n> ").strip().lower()
            if choice2 == "exit":
                print("Cancelled.")
            elif choice2.isdigit() and 1 <= int(choice2) <= len(items):
                deleted = items[int(choice2) - 1]
                delete_food_from_meal(deleted["id"])
                print(f"Deleted {deleted['food_name']} from '{selected_meal}'.")
            else:
                print("Invalid choice.")

        elif command == "summary":
            print_summary(date)

        else:
            print("Unknown command. Available: 'meal <name>', 'switch <name>', "
                  "'search <food>', 'select <number> <grams>', "
                  "'delete meal', 'delete food', 'summary', 'where', 'exit', 'back'")