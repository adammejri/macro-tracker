from db.meal_repo import (
    get_meals_for_date,
    get_foods_in_meal,
    insert_meal_entry,
    delete_meal,
    delete_food_entry,
    get_daily_meal_totals
)

def search_and_prepare_food(food_row, grams):
    factor = grams / 100
    return {
        "name":     food_row["name"],
        "brand":    food_row["brand"],
        "grams":    grams,
        "calories": round(food_row["calories"] * factor, 1),
        "protein":  round(food_row["protein"]  * factor, 1),
        "carbs":    round(food_row["carbs"]    * factor, 1),
        "fat":      round(food_row["fat"]      * factor, 1)
    }

def add_food_to_meal(date, meal_name, food_row, grams):
    food = search_and_prepare_food(food_row, grams)
    insert_meal_entry(date, meal_name, food)
    return food

def remove_meal(date, meal_name):
    delete_meal(date, meal_name)

def remove_food(food_id):
    delete_food_entry(food_id)

def get_meal_summary(date):
    meals = get_meals_for_date(date)
    result = []

    for meal_row in meals:
        meal_name = meal_row["meal_name"]
        items = get_foods_in_meal(date, meal_name)
        meal_totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        food_list = []
        for item in items:
            food_list.append(dict(item))
            meal_totals["calories"] += item["calories"]
            meal_totals["protein"]  += item["protein"]
            meal_totals["carbs"]    += item["carbs"]
            meal_totals["fat"]      += item["fat"]

        result.append({
            "meal_name": meal_name,
            "foods": food_list,
            "totals": {k: round(v, 1) for k, v in meal_totals.items()}
        })

    return result

def get_daily_totals(date):
    row = get_daily_meal_totals(date)
    if not row:
        return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    return {
        "calories": row["total_calories"] or 0,
        "protein":  row["total_protein"]  or 0,
        "carbs":    row["total_carbs"]    or 0,
        "fat":      row["total_fat"]      or 0
    }