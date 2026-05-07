from db.nutrition_repo import search_foods, insert_food, get_all_foods

def find_foods(query):
    return search_foods(query)

def add_food(name, brand, calories, protein, carbs, fat):
    insert_food(name, brand, calories, protein, carbs, fat)

def list_all_foods():
    return get_all_foods()