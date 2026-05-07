from datetime import date as today_date
from cli.meal_cli import run_meal_cli, print_summary
from cli.activity_cli import run_activity_cli
from core.summary_service import get_full_day_summary, get_all_dates, date_has_data
from db.activity_repo import get_daily_info
from core.activity_service import get_activities
import cli.state as state

def print_day_summary(date):
    summary = get_full_day_summary(date)

    print(f"\n=== Summary for {date} ===")

    info = summary["info"]
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

    activities = summary["activities"]
    if activities:
        print(f"\nActivities:")
        for act in activities:
            if act["distance_km"]:
                print(f"  {act['activity_type']}: {act['distance_km']} km "
                      f"— {act['calories_burned']} kcal")
            else:
                print(f"  {act['activity_type']}: {act['duration_minutes']} min "
                      f"— {act['calories_burned']} kcal")

    print_summary(date)

def menu_past_days():
    state.push("Past Days")
    while True:
        print(f"\n[{state.where()}]")
        dates = get_all_dates()

        if not dates:
            print("No recorded days found.")
            state.pop()
            return

        for i, row in enumerate(dates, 1):
            print(f"{i}. {row['date']}")
        print("\nType a number, a date (YYYY-MM-DD), 'where', or 'exit'.")

        choice = input("\n> ").strip()
        choice_lower = choice.lower()

        result = state.check_global(choice_lower)
        if result == "commands":
            print("Commands: number, YYYY-MM-DD date, 'where', 'back to main', 'exit'")
            continue
        elif result:
            continue

        choice = choice_lower

        if choice == "back to main":
            state.pop()
            print("Returning to main menu.")
            break

        elif choice == "exit":
            state.pop()
            break

        elif choice.isdigit() and 1 <= int(choice) <= len(dates):
            selected_date = dates[int(choice) - 1]["date"]
            menu_day_detail(selected_date)

        else:
            try:
                from datetime import datetime
                datetime.strptime(choice, "%Y-%m-%d")
                if date_has_data(choice):
                    menu_day_detail(choice)
                else:
                    print(f"No data found for {choice}.")
                    create = input("Log data for this day? (yes/no): ").strip().lower()
                    if create == "yes":
                        menu_day_detail(choice, new_day=True)
            except ValueError:
                print("Invalid input. Use a number or YYYY-MM-DD.")

def menu_day_detail(date, new_day=False):
    if new_day:
        print(f"\nCreating new entry for {date}.")

    state.push(f"Day:{date}")
    while True:
        print(f"\n[{state.where()}]")
        print("1. Log meals")
        print("2. Log activities")
        print("3. View summary")
        print("4. Exit")

        choice = input("\n> ").strip()
        choice_lower = choice.lower()

        result = state.check_global(choice)
        if result == "commands":
            print("Commands: 1-4, 'where', 'back to main'")
            continue
        elif result:
            continue
        
        if choice_lower == "back to main":
            state.pop()
            print("Returning to main menu.")
            break
        elif choice_lower == "exit":
            state.pop()
            break
        elif choice == "1":
            state.push("Meal Logger")
            run_meal_cli(date)
            state.pop()
        elif choice == "2":
            state.push("Activity Logger")
            run_activity_cli(date)
            state.pop()
        elif choice == "3":
            print_day_summary(date)
        elif choice == "4":
            state.pop()
            break
        else:
            print("Invalid choice.")

def main():
    state.reset()
    state.push("Main Menu")
    today = str(today_date.today())

    print("=" * 40)
    print("       MACRO & ACTIVITY TRACKER")
    print("=" * 40)
    print(f"Today: {today}")
    print("Type 'commands' to see available options.")

    while True:
        print(f"\n[{state.where()}]")
        print("1. Log meals")
        print("2. Log activities & calculate TDEE")
        print("3. View past days")
        print("4. Today's summary")
        print("5. Exit")

        choice = input("\n> ").strip()
        choice_lower = choice.lower()

        result = state.check_global(choice)
        if result == "commands":
            print("\nCommands: 1-5, 'where', 'commands'")
            continue
        elif result:
            continue

        if choice == "1":
            state.push("Meal Logger")
            run_meal_cli(today)
            state.pop()
        elif choice == "2":
            state.push("Activity Logger")
            run_activity_cli(today)
            state.pop()
        elif choice == "3":
            menu_past_days()
        elif choice == "4":
            print_day_summary(today)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Pick 1-5.")

if __name__ == "__main__":
    main()