import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def create_connection():
    """Create a database connection to the SQLite database specified by db_file."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_tables():
    """Create the necessary tables if they don't already exist."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            default_city TEXT
        )
    ''')
    conn.commit()
    conn.close()


def set_default_city(user_id, city):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            existing_city = get_default_city(user_id, cursor)
            print(f"Existing city for user {user_id}: {existing_city}")
            if existing_city:
                cursor.execute("UPDATE users SET default_city=? WHERE user_id=?", (city, user_id))
                print(f"Updated city for user {user_id} to {city}")
            else:
                cursor.execute("INSERT INTO users (user_id, default_city) VALUES (?, ?)", (user_id, city))
                print(f"Inserted city for user {user_id}: {city}")
            conn.commit()
    except Exception as e:
        print(f"Error setting default city: {e}")


def get_default_city(user_id, cursor):
    cursor.execute("SELECT default_city FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None
