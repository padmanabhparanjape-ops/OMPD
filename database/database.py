import sqlite3
from datetime import datetime


DB_NAME = "detections.db"


def create_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

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
    conn.close()


def insert_detection(object_name, confidence, action):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO detections(time, object, confidence, action)
    VALUES (?, ?, ?, ?)
    """,
    (time, object_name, confidence, action))

    conn.commit()
    conn.close()


def get_all_detections():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM detections")

    data = cursor.fetchall()

    conn.close()

    return data


if __name__ == "__main__":

    create_database()

    insert_detection(
        "Phone",
        0.95,
        "Blurred"
    )

    print(get_all_detections())