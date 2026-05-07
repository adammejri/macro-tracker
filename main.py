from datetime import date as today_date
import state 
from meal_logger import run_meal_logger, print_summary, get_daily_totals, get_targets_for_date
from activity_logger import run_activity_logger, get_activities
from db import get_logs_db

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_all_logged_dates():
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT DISTINCT date FROM daily_info ORDER BY date DESC
        """).fetchall()

def date_exists(date):
    with get_logs_db() as conn:
        row = conn.execute(
            "SELECT date FROM daily_info WHERE date = ?", (date,)
        ).fetchone()
        return row is not None

def print_day_summary(date):
    print(f"\n=== Summary for {date} ===")

    with get_logs_db() as conn:
        info = conn.execute(
            "SELECT * FROM daily_info WHERE date = ?", (date,)
        ).fetchone()

    if info:
        print(f"\nWeight:  {info['weight']} kg")
        print(f"Steps:   {info['steps']}")
        print(f"TDEE:    {info['tdee']} kcal")
        print(f"BMR:     {info['bmr']} kcal")
        print(f"\nTargets:")
        print(f"  Calories: {info['calorie_target']} kcal")
        print(f"  Protein:  {info['protein_target']}g")
        print(f"  Carbs:    {info['carbs_target']}g")
        print(f"  Fat:      {info['fat_target']}g")

    activities = get_activities(date)
    if activities:
        print(f"\nActivities:")
        for act in activities:
            if act["distance_km"]:
                print(f"  {act['activity_type']}: {act['distance_km']} km — {act['calories_burned']} kcal")
            else:
                print(f"  {act['activity_type']}: {act['duration_minutes']} min — {act['calories_burned']} kcal")

    print_summary(date)

# ─── SUBMENUS ─────────────────────────────────────────────────────────────────

def menu_log_meals(date):
    run_meal_logger(date=date)

def menu_log_activities(date):
    run_activity_logger(date=date)

def menu_past_days():
    while True:
        print("\n--- Recorded Days ---")
        dates = get_all_logged_dates()

        if not dates:
            print("No recorded days found.")
            return

        for i, row in enumerate(dates, 1):
            print(f"{i}. {row['date']}")
        print("Type a number to view a day, enter a date (YYYY-MM-DD) to look up, or 'exit'.")

        choice = input("\n> ").strip().lower()

        if state.check_global(choice):
            continue
        
        elif choice == "exit":
            break

        elif choice.isdigit() and 1 <= int(choice) <= len(dates):
            selected_date = dates[int(choice) - 1]["date"]
            state.push(f"Day:{selected_date}")
            menu_day_detail(selected_date)
            state.pop()

        else:
            try:
                from datetime import datetime
                datetime.strptime(choice, "%Y-%m-%d")
                if date_exists(choice):
                    menu_day_detail(choice)
                else:
                    print(f"No data found for {choice}.")
                    create = input("Would you like to log data for this day? (yes/no): ").strip().lower()
                    if create == "yes":
                        menu_day_detail(choice, new_day=True)
            except ValueError:
                print("Invalid input. Use a number or date format YYYY-MM-DD.")

def menu_day_detail(date, new_day=False):
    if new_day:
        print(f"\nCreating new entry for {date}.")

    while True:
        print(f"\n--- {date} ---")
        print("1. Log meals")
        print("2. Log activities")
        print("3. View summary")
        print("4. Exit")

        choice = input("\n> ").strip()

        if state.check_global(choice):
            continue
        elif choice == "1":
            state.push("Meal Logger")
            menu_log_meals(date)
            state.pop()
        elif choice == "2":
            state.push("Activity Logger")
            menu_log_activities(date)
            state.pop()
        elif choice == "3":
            print_day_summary(date)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

# ─── MAIN MENU ────────────────────────────────────────────────────────────────

def main():
    state.reset()
    state.push("Main Menu")

    today = str(today_date.today())

    print("=" * 40)
    print("       MACRO & ACTIVITY TRACKER")
    print("=" * 40)
    print(f"Today: {today}")

    while True:
        print("\n--- Main Menu ---")
        print("1. Log meals")
        print("2. Log activities & calculate TDEE")
        print("3. View past days")
        print("4. Today's summary")
        print("5. Exit")

        choice = input("\n> ").strip()
        
        if state.check_global(choice):
            continue
        elif choice == "1":
            state.push("Meal Logger")
            menu_log_meals(today)
            state.pop()
        elif choice == "2":
            state.push("Activity Logger")
            menu_log_activities(today)
            state.pop()
        elif choice == "3":
            state.push("Past Days")
            menu_past_days()
            state.pop()
        elif choice == "4":
            print_day_summary(today)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Pick 1-5.")

if __name__ == "__main__":
    main()