import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'users.db'

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_user(first_name, last_name, email, password):
    conn = get_conn()
    cur  = conn.cursor()
    hashed = generate_password_hash(password)
    cur.execute('INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)',
                (first_name, last_name, email, hashed))
    conn.commit()
    conn.close()

def authenticate(email, password):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute('SELECT password FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

def get_user(email):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute('SELECT id, first_name, last_name, email FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    return user  # (id, first_name, last_name, email) or None
