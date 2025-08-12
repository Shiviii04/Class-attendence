import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        hashed = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False
