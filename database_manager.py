import os
import sqlite3

import config
from logger import logger # import logger


# Створюємо директорію для БД, якщо її немає
if not os.path.exists(config.DB_DIR):
    try:
        os.makedirs(config.DB_DIR)
        logger.info(f"Created database directory: {config.DB_DIR}")
    except OSError as e:
        logger.critical(f"Failed to create database directory {config.DB_DIR}: {e}", exc_info=True)
        raise Exception(f"Failed to create database directory {config.DB_DIR}: {e}")


def execute_query(query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False):
    """
    Executes an SQL query and handles connection, cursor, commit.
    Optionally fetches one or all results.
    Ensures foreign key constraints are enabled for each connection.
    """
    
    conn = None 
    try:
        conn = sqlite3.connect(database=config.DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;") # Ввімкнення підтримки зовнішніх ключів (FOREIGN KEYs)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        
        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
        else:
            return None
    except sqlite3.Error as e:
        logger.error(f"Database error during query execution: {e}", exc_info=True)
        raise 
    finally:
        if conn:
            conn.close()


# Ініціалізація БД (створить таблицю, якщо вона ще не існує)
# Init Database
def init_database():
    """
    Creates necessary tables (users and birthdays) if they do not already exist.
    Called at bot startup.
    """
    
    logger.info("Initializing database tables...")

    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_user_id INTEGER PRIMARY KEY UNIQUE NOT NULL,   -- Унікальний Telegram ID користувача
            telegram_user_name TEXT NOT NULL,   -- Ім'я користувача бота (його повне ім'я з Telegram)
            telegram_user_tag TEXT  -- @username користувача бота (може бути NULL)
        )
    """)
    logger.info("Table 'users' checked/created.")

    # Таблиця CHATS 
    execute_query("""
        CREATE TABLE IF NOT EXISTS chats (
            telegram_chat_id INTEGER UNIQUE NOT NULL,
            telegram_chat_name TEXT NOT NULL,
            telegram_chat_type TEXT NOT NULL -- Тип чату (e.g., 'private', 'group', 'supergroup')
        )
    """)
    logger.info("Table 'chats' checked/created.")

    # Таблиця BIRTHDAYS з зовнішніми ключами
    execute_query("""
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Поле для того, хто додав нагадування
            creator_telegram_user_id INTEGER NOT NULL,

            -- Поле для юзера, в якого день народження
            birthday_person_identifier TEXT NOT NULL,
            
            birthdate TEXT NOT NULL, -- Формат YYYY-MM-DD або MM-DD
            telegram_chat_id INTEGER NOT NULL, -- Куди надсилати нагадування
            
            -- Пов'язати таблиці
            FOREIGN KEY (creator_telegram_user_id) REFERENCES users (telegram_user_id) ON DELETE CASCADE
            FOREIGN KEY (telegram_chat_id) REFERENCES chats (telegram_chat_id) ON DELETE CASCADE
        )
    """)
    logger.info("Table 'birthdays' checked/created.")


def add_or_update_user(telegram_user_id: int, telegram_user_name: str, telegram_user_tag: str = None):
    """
    Додає нового користувача або оновлює інформацію існуючого користувача в таблиці 'users'.
    Використовує ON CONFLICT(telegram_user_id).
    
    Args:
        telegram_user_id (int): Унікальний Telegram ID користувача.
        telegram_user_name (str): Ім'я користувача.
        telegram_user_tag (str, optional): Telegram @username користувача. За замовчуванням None.
    """
    query = """
        INSERT INTO users (telegram_user_id, telegram_user_name, telegram_user_tag)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_user_id) DO UPDATE SET
            telegram_user_name = EXCLUDED.telegram_user_name,
            telegram_user_tag = EXCLUDED.telegram_user_tag;
    """
    params = (telegram_user_id, telegram_user_name, telegram_user_tag)
    execute_query(query, params)
    logger.info(f"User {telegram_user_name} (ID: {telegram_user_id}) added/updated in DB (Tag: {telegram_user_tag}).")


def add_or_update_chat_info(telegram_chat_id: int, telegram_chat_name: str = None, telegram_chat_type: str = 'private'):
    """
    Додає новий чат або оновлює інформацію існуючого чату в таблиці 'chats'.
    Використовує ON CONFLICT(telegram_chat_id).
    
    Args:
        telegram_chat_id (int): Унікальний Telegram ID чату.
        telegram_chat_name (str, optional): Назва чату. За замовчуванням None.
        telegram_chat_type (str): Тип чату (e.g., 'private', 'group', 'supergroup'). За замовчуванням 'private'.
    """
    query = """
        INSERT INTO chats (telegram_chat_id, telegram_chat_name, telegram_chat_type)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_chat_id) DO UPDATE SET
            telegram_chat_name = EXCLUDED.telegram_chat_name,
            telegram_chat_type = EXCLUDED.telegram_chat_type;
    """
    params = (telegram_chat_id, telegram_chat_name, telegram_chat_type)
    execute_query(query, params)
    logger.info(f"Chat '{telegram_chat_name}' (ID: {telegram_chat_id}, Type: {telegram_chat_type}) added/updated in DB.")


def add_birthday_reminder(
    creator_telegram_user_id: int,
    birthday_person_identifier: str, 
    birthdate: str, 
    telegram_chat_id: int
):
    """
    Додає нове нагадування про день народження до таблиці 'birthdays'.
    Зв'язується з існуючим user_id у таблиці 'users'.
    """

    query = """
        INSERT INTO birthdays (
            creator_telegram_user_id, 
            birthday_person_identifier,
            birthdate, 
            telegram_chat_id
        )
        VALUES (?, ?, ?, ?)
    """
    params = (creator_telegram_user_id, birthday_person_identifier, birthdate, telegram_chat_id)
    execute_query(query, params)
    logger.info(f"Birthday reminder added for user ID {birthday_person_identifier} (birthdate: {birthdate}) to notify chat {telegram_chat_id}.")


def get_birthday_reminders_for_today():
    """
    Retrieves all birthday reminders for today from the 'birthdays' table.
    Joins with 'users' table to get the user's name and Telegram tag.
    Returns a list of (user_id, name, telegram_tag, chat_id_to_notify) tuples.
    """
    
    logger.info("Retrieving today's birthday reminders from the database...")
    
    # SQL-запит, який об'єднує таблиці 'birthdays' та 'chats'
    # Це дозволяє отримати ім'я чи тег користувача, чий день народження.
    query = """
        SELECT 
            b.id,
            b.creator_telegram_user_id,
            b.birthday_person_identifier,
            b.birthdate,
            b.telegram_chat_id,
            c.telegram_chat_name,
            c.telegram_chat_type
        FROM birthdays b
        JOIN chats c ON b.telegram_chat_id = c.telegram_chat_id
        WHERE STRFTIME('%m-%d', b.birthdate) = STRFTIME('%m-%d', 'now', 'localtime');
    """
    
    reminders = execute_query(query, fetchall=True)
    logger.debug(f"Found {len(reminders)} birthday reminders for today.")
    
    # Повертає список кортежів, де кожен кортеж містить певні визначені поля
    return reminders