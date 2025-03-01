import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "grader.db")


def initialize_database():
    create_file_url = os.path.join(os.path.dirname(__file__), "grader_create.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(create_file_url, "r") as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()


def get_container(course_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute(
        "SELECT containerUrl FROM courses WHERE coursename=?", (course_name,)
    )
    return res.fetchone()[0]


def upsert_course(course_name, container_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = """
        INSERT INTO courses (coursename, containerUrl)
        VALUES (?, ?)
        ON CONFLICT(coursename) DO UPDATE 
        SET containerUrl = excluded.containerUrl
    """
    cursor.execute(sql, (course_name, container_name))
    conn.commit()
    conn.close()


def fetch_students():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM students")
    return res.fetchall()


def fetch_courses():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("SELECT id, coursename, containerUrl FROM courses")
    return res.fetchall()

if __name__ == "__main__":
    initialize_database()
