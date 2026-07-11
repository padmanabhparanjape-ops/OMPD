import sqlite3
from datetime import datetime


class Database:

    def __init__(self, db_name="database/privacy_logs.db"):

        self.connection = sqlite3.connect(db_name)

        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            event_type TEXT,

            label TEXT,

            confidence REAL

        )
        """)

        self.connection.commit()

    def log_detection(
        self,
        event_type,
        label,
        confidence
    ):

        self.cursor.execute(

            """
            INSERT INTO detections
            (
                timestamp,
                event_type,
                label,
                confidence
            )
            VALUES (?, ?, ?, ?)
            """,

            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event_type,
                label,
                confidence
            )
        )

        self.connection.commit()

    def close(self):
        self.connection.close()