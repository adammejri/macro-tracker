import sqlite3
from contextlib import contextmanager
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NUTRITION_DB = os.path.join(BASE_DIR, "databases", "nutrition.db")
LOGS_DB = os.path.join(BASE_DIR, "databases", "logs.db")

@contextmanager
def get_nutrition_db():
    conn = sqlite3.connect(NUTRITION_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@contextmanager
def get_logs_db():
    conn = sqlite3.connect(LOGS_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()