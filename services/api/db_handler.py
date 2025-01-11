from db.database import create_database
from db.database_utils import create_submission


def initialize_db():
    create_database()


def submission_id():
    return create_submission()
