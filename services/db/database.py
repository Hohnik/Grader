import os
import sqlite3


def create_database():
    db_path = os.path.join(os.path.dirname(__file__), "grader.db")
    create_file_url = os.path.join(os.path.dirname(__file__), "grader_create.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(create_file_url, "r") as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()


create_database()
