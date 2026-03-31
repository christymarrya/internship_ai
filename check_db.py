import sqlite3

conn = sqlite3.connect("internai.db")
cursor = conn.cursor()
cursor.execute("SELECT email, hashed_password FROM users WHERE email='test@example.com'")
row = cursor.fetchone()
print(f"DB Record: {row}")
conn.close()
