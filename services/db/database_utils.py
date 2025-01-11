import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "grader.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


def create_submission():
    cursor.execute("BEGIN TRANSACTION;")
    try:
        cursor.execute("INSERT INTO submissions DEFAULT VALUES;")
        new_id = cursor.lastrowid
        conn.commit()
        return new_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
