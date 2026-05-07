from db.connection import get_logs_db

def get_daily_info(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT * FROM daily_info WHERE date = ?
        """, (date,)).fetchone()

def get_last_daily_info():
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT * FROM daily_info ORDER BY date DESC LIMIT 1
        """).fetchone()

def upsert_daily_info(date, weight, height, age, gender, steps, tdee, bmr,
                      protein_target, carbs_target, fat_target, calorie_target):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT INTO daily_info (date, weight, height, age, gender, steps, tdee, bmr,
                                   protein_target, carbs_target, fat_target, calorie_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                weight=excluded.weight,
                height=excluded.height,
                age=excluded.age,
                gender=excluded.gender,
                steps=excluded.steps,
                tdee=excluded.tdee,
                bmr=excluded.bmr,
                protein_target=excluded.protein_target,
                carbs_target=excluded.carbs_target,
                fat_target=excluded.fat_target,
                calorie_target=excluded.calorie_target
        """, (date, weight, height, age, gender, steps, tdee, bmr,
              protein_target, carbs_target, fat_target, calorie_target))

def get_targets_for_date(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT calorie_target, protein_target, carbs_target, fat_target
            FROM daily_info WHERE date = ?
        """, (date,)).fetchone()

def insert_activity(date, activity_type, duration, distance, calories_burned):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT INTO activity_logs (date, activity_type, duration_minutes, distance_km, calories_burned)
            VALUES (?, ?, ?, ?, ?)
        """, (date, activity_type, duration, distance, calories_burned))

def get_activities_for_date(date):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT * FROM activity_logs WHERE date = ?
        """, (date,)).fetchall()

def delete_activity(activity_id):
    with get_logs_db() as conn:
        conn.execute("DELETE FROM activity_logs WHERE id = ?", (activity_id,))

def get_all_activity_types():
    with get_logs_db() as conn:
        return conn.execute("SELECT * FROM activity_types").fetchall()

def get_activity_type(name):
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT * FROM activity_types WHERE name = ?
        """, (name,)).fetchone()

def insert_activity_type(name, metric, met_value=None, kcal_per_kg_per_km=None):
    with get_logs_db() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO activity_types (name, metric, met_value, kcal_per_kg_per_km)
            VALUES (?, ?, ?, ?)
        """, (name, metric, met_value, kcal_per_kg_per_km))

def get_all_logged_dates():
    with get_logs_db() as conn:
        return conn.execute("""
            SELECT DISTINCT date FROM daily_info ORDER BY date DESC
        """).fetchall()