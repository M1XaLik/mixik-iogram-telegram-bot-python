import os
import sqlite3

# Отримуємо абсолютний шлях до файлу бази даних
DB_PATH = os.path.join("data", "botbase.db")

# Connect DATABASE
def execute_query(query, params=(), fetchone=False):
    with sqlite3.connect(database=DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchone() if fetchone else cursor.fetchall()

# Ініціалізація БД
# Init Database
def init_database():
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            name TEXT,
            birthdate TEXT
        )
    """)

def add_user(user_id, name, birthdate):
    execute_query("string")

# def get_user(user_id):
#     execute_query("string")

def users_list(chat_id):
    execute_query("string")