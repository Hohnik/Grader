from db.database import (_create_submission, _delete_course_by_id,
                         _fetch_courses, _fetch_students,
                         _get_container_by_name, _get_student_by_name,
                         _initialize_database, _update_submission,
                         _upsert_course_by_name)


def init_db():
    _initialize_database()


def create_submission():
    return _create_submission()

def update_submission(score):
    return _update_submission(score)

def get_container_by_name(course_name):
    return _get_container_by_name(course_name)


def upsert_course_by_name(course_name, container_name):
    return _upsert_course_by_name(course_name, container_name)


def fetch_students():
    return _fetch_students()


def fetch_courses():
    return _fetch_courses()


def delete_course_by_id(id):
    return _delete_course_by_id(id)

def get_course_by_name(course_name):
    return _get_student_by_name(course_name)
