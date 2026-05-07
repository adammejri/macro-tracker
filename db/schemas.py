NUTRITION_SCHEMA = """
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY,
    name TEXT,
    brand TEXT,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL
);
"""

LOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_info (
    date TEXT PRIMARY KEY,
    weight REAL,
    height REAL,
    age INTEGER,
    gender TEXT,
    steps INTEGER,
    tdee REAL,
    bmr REAL,
    protein_target REAL,
    carbs_target REAL,
    fat_target REAL,
    calorie_target REAL
);

CREATE TABLE IF NOT EXISTS meal_logs (
    id INTEGER PRIMARY KEY,
    date TEXT,
    meal_name TEXT,
    food_name TEXT,
    brand TEXT,
    grams REAL,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL,
    FOREIGN KEY (date) REFERENCES daily_info(date)
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY,
    date TEXT,
    activity_type TEXT,
    duration_minutes REAL,
    distance_km REAL,
    calories_burned REAL,
    FOREIGN KEY (date) REFERENCES daily_info(date)
);

CREATE TABLE IF NOT EXISTS activity_types (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    metric TEXT,
    met_value REAL,
    kcal_per_kg_per_km REAL
);
"""

DEFAULT_ACTIVITY_TYPES = [
    ("gym",          "duration", 4.5,  None),
    ("sparring",     "duration", 12.8, None),
    ("boxing_class", "duration", 9.0,  None),
    ("football",     "duration", 8.8,  None),
    ("run_zone2",    "distance", None, 1.0),
    ("run_interval", "distance", None, 1.15),
]