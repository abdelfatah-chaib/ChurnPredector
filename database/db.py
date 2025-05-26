import sqlite3

DB_PATH = 'database/users.db'

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_user(first_name, last_name, email, password):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute('INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)',
                (first_name, last_name, email, password))
    conn.commit()
    conn.close()

def authenticate(email, password):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute('SELECT password FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return row is not None and row[0] == password

def get_user(email):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute('SELECT id, first_name, last_name, email FROM users WHERE email = ?', (email,))
    user = cur.fetchone()
    conn.close()
    return user
