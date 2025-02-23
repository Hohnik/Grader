import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "grader.db")


def create_database():
    create_file_url = os.path.join(os.path.dirname(__file__), "grader_create.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(create_file_url, "r") as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()


def fetch_container(course_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute(
        "SELECT containerUrl FROM courses WHERE coursename=?", (course_name,)
    )
    return res.fetchone()[0]


if __name__ == "__main__":
    create_database()
