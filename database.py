import sqlite3

# Initialize the database and tables
def init_db():
    conn = sqlite3.connect('scan_and_go.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Create attendance table
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY,
        student_id TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

# Add user to the database
def add_user(username, email, password):
    conn = sqlite3.connect('scan_and_go.db')
    c = conn.cursor()
    
    # Check if username already exists
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone():
        return False  # Username already exists
    
    c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()
    conn.close()
    return True

# Verify user credentials
def verify_user(username, password):
    conn = sqlite3.connect('scan_and_go.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Log attendance in the database
def log_attendance(student_id):
    conn = sqlite3.connect('scan_and_go.db')
    c = conn.cursor()
    c.execute('INSERT INTO attendance (student_id) VALUES (?)', (student_id,))
    conn.commit()
    conn.close()
