from db.connection import get_logs_db

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

def insert_meal_entry(date, meal_name, food):
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

def delete_food_entry(food_id):
    with get_logs_db() as conn:
        conn.execute("DELETE FROM meal_logs WHERE id = ?", (food_id,))

def get_daily_meal_totals(date):
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