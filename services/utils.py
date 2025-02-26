def course_ok(course):
    with open("db/courses.txt", "r") as f:
        return course in [line.strip() for line in f]


def student_ok(name):
    with open("db/students.txt", "r") as f:
        return name in [line.strip() for line in f]
