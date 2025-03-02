from db.database import (
    delete_course,
    fetch_courses,
    fetch_students,
    get_container,
    initialize_database,
    upsert_course,
)
from db.database_utils import create_submission


def init_db():
    initialize_database()


def get_submission_id():
    return create_submission()


def get_container_by_course_name(course_name):
    return get_container(course_name)


def upsert_course_by_course_name(course_name, container_name):
    return upsert_course(course_name, container_name)


def fetch_all_students():
    return fetch_students()


def fetch_all_courses():
    return fetch_courses()


def delete_course_by_id(id):
    return delete_course(id)
