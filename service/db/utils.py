import sqlite3

conn = sqlite3.connect("db/grader.db")
cursor = conn.cursor()


def next_id() -> int:
    cursor.execute("BEGIN TRANSACTION;")
    try:
        cursor.execute("SELECT id FROM global_id;")
        current_id = cursor.fetchone()[0]
        new_id = current_id + 1

        cursor.execute("UPDATE global_id SET id = ?;", (new_id))
        conn.commit()

        return new_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return 0
