import sqlite3

# Connect to database (creates it if it doesn't exist)
conn = sqlite3.connect("detections.db")

# Cursor object
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS detections(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    object TEXT,
    confidence REAL,
    action TEXT
)
""")

conn.commit()

print("Database and table created successfully.")

conn.close()