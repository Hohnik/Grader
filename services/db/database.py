import os
import sqlite3
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "grader.db")


def _initialize_database():
    create_file_url = os.path.join(os.path.dirname(__file__), "grader_create.sql")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(create_file_url, "r") as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    conn.commit()
    conn.close()

def _create_submission():
    """ Returns the id of the created submission """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("BEGIN TRANSACTION;")
    try:
        cursor.execute("INSERT INTO submissions DEFAULT VALUES;")
        new_id = cursor.lastrowid
        conn.commit()
        return new_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")

def _update_submission(score):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql = """
        UPDATE submissions 
        SET score=?, timestamp=?
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(sql, (score, timestamp))
    conn.commit()
    conn.close()


def _get_container_by_name(course_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute(
        "SELECT containerUrl FROM courses WHERE coursename=?", (course_name,)
    )
    return res.fetchone()[0]


def _upsert_course_by_name(course_name, container_name):
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


def _fetch_students():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("SELECT * FROM students")
    return res.fetchall()


def _fetch_courses():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("SELECT id, coursename, containerUrl FROM courses")
    return res.fetchall()


def _get_student_by_name(student_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("""
        SELECT id, username
        FROM students 
        WHERE username=?
    """, (student_name,))
    return res.fetchone()


def _get_student_by_name(course_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    res = cursor.execute("""
        SELECT id, coursename, containerUrl 
        FROM courses 
        WHERE coursename=?
    """, (course_name,))
    return res.fetchone()

def _delete_course_by_id(id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        sql = """
            DELETE FROM courses
            WHERE id = ?
        """
        cursor.execute(sql, (id,))
        conn.commit()
        rows_deleted = cursor.rowcount
    except sqlite3.Error as e:
        print("SQLite error:", e)
        rows_deleted = 0
    finally:
        conn.close()

    return rows_deleted > 0


if __name__ == "__main__":
    _initialize_database()
