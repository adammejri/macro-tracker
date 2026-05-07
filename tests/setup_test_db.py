import sqlite3
import os

os.makedirs("databases", exist_ok=True)

conn = sqlite3.connect("databases/nutrition.db")
conn.execute("""CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    name TEXT, brand TEXT,
    calories REAL, protein REAL,
    carbs REAL, fat REAL
)""")
conn.commit()
conn.close()

conn2 = sqlite3.connect("databases/logs.db")
conn2.execute("""CREATE TABLE IF NOT EXISTS daily_info (
    date TEXT PRIMARY KEY, weight REAL, height REAL,
    age INTEGER, gender TEXT, steps INTEGER,
    tdee REAL, bmr REAL, protein_target REAL,
    carbs_target REAL, fat_target REAL, calorie_target REAL
)""")
conn2.execute("""CREATE TABLE IF NOT EXISTS meal_logs (
    id INTEGER PRIMARY KEY, date TEXT, meal_name TEXT,
    food_name TEXT, brand TEXT, grams REAL,
    calories REAL, protein REAL, carbs REAL, fat REAL,
    FOREIGN KEY (date) REFERENCES daily_info(date)
)""")
conn2.execute("""CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY, date TEXT, activity_type TEXT,
    duration_minutes REAL, distance_km REAL, calories_burned REAL,
    FOREIGN KEY (date) REFERENCES daily_info(date)
)""")
conn2.execute("""CREATE TABLE IF NOT EXISTS activity_types (
    id INTEGER PRIMARY KEY, name TEXT UNIQUE,
    metric TEXT, met_value REAL, kcal_per_kg_per_km REAL
)""")
conn2.commit()
conn2.close()
print("Test databases created.")