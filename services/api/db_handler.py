from db.database import get_container, initialize_database, upsert_course
from db.database_utils import create_submission


def init_db():
    initialize_database()


def get_submission_id():
    return create_submission()


def get_container_by_course_name(course_name):
    return get_container(course_name)

def upsert_course_by_course_name(course_name, container_name):
    return upsert_course(course_name, container_name)

