import os

from db.utils import next_id


def course_ok(course):
    with open("db/courses.txt", "r") as f:
        return course in [line.strip() for line in f]


def student_ok(name):
    with open("db/students.txt", "r") as f:
        return name in [line.strip() for line in f]


def save_submission(student, course, zipfile) -> int:
    task_id = next_id()

    os.makedirs(f"submissions/{course}/{student}", exist_ok=True)
    with open(f"submissions/{course}/{student}/{task_id}.zip", "wb") as f:
        f.write(zipfile.file.read())

    return task_id
