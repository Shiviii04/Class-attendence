from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os, csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'users.db'
ATTENDANCE_FILE = 'attendance.csv'

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('scanner'))
            flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/scanner')
def scanner():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('scanner.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'username' not in session:
        return redirect(url_for('login'))

    scanned_id = request.form['scanned_id']
    now = datetime.now()
    date, time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Scanned ID', 'Username', 'Date', 'Time'])

    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([scanned_id, session['username'], date, time])

    flash('Attendance marked.')
    return redirect(url_for('scanner'))

@app.route('/attendance')
def attendance():
    if 'username' not in session:
        return redirect(url_for('login'))
    rows = []
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            rows = list(reader)
    return render_template('attendance.html', records=rows)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # In a real app, you would send a reset email or similar
        flash(f'If an account with username "{username}" and email "{email}" exists, password reset instructions will be sent to that email.')
        return redirect(url_for('login'))
    return render_template('forgot-password.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
