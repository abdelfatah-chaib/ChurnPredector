import sqlite3

conn = sqlite3.connect('users.db')
cur  = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("✅ Base users.db recréée sans hash.")
# This script initializes the database for user management.