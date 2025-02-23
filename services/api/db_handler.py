from db.database import create_database, fetch_container
from db.database_utils import create_submission


def initialize_db():
    create_database()


def submission_id():
    return create_submission()


def get_container_url(course_name):
    return fetch_container(course_name)
