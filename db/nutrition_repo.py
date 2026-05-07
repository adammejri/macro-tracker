from db.connection import get_nutrition_db

def search_foods(query):
    with get_nutrition_db() as conn:
        return conn.execute("""
            SELECT id, name, brand, calories, protein, carbs, fat
            FROM foods
            WHERE LOWER(name) LIKE ? OR LOWER(brand) LIKE ?
        """, (f"%{query}%", f"%{query}%")).fetchall()

def insert_food(name, brand, calories, protein, carbs, fat):
    with get_nutrition_db() as conn:
        conn.execute("""
            INSERT INTO foods (name, brand, calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, brand, calories, protein, carbs, fat))

def get_all_foods():
    with get_nutrition_db() as conn:
        return conn.execute("""
            SELECT id, name, brand, calories, protein, carbs, fat
            FROM foods
            ORDER BY name
        """).fetchall()