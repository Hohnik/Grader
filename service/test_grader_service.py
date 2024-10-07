import unittest
import os
import tempfile
from grader_service import app, UPLOAD_FOLDER
from io import BytesIO

class GraderServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.app.config['upload_folder'] = tempfile.mkdtemp()
        self.client = self.app.test_client()

        # Backup original content (assume files always exist)
        with open('students.txt', 'r') as f:
            self.students_backup = f.read()

        with open('courses.txt', 'r') as f:
            self.courses_backup = f.read()

        # Create temporary files for students and courses
        with open('students.txt', 'w') as f:
            f.write('s-nhohnn\n')
        with open('courses.txt', 'w') as f:
            f.write('Programmieren III\n')

    def tearDown(self):
        # Restore the original content
        with open('students.txt', 'w') as f:
            f.write(self.students_backup)

        with open('courses.txt', 'w') as f:
            f.write(self.courses_backup)


    def test_submit_valid_project(self):
        data = {
            'student_name': 's-nhohnn',
            'course_name': 'Programmieren III'
        }
        file_content = b'This is a test zip file'
        file_data = {
            'submission': (BytesIO(file_content), 'test.zip')
        }

        response = self.client.post('/submit', data={**data, **file_data}, content_type='multipart/form-data')

        print(response.text)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Submission successful', response.data)

    def test_submit_invalid_student(self):
        data = {
            'student_name': 'invalid_student',
            'course_name': 'python_101'
        }
        file_content = b'This is a test zip file'
        data['submission'] = (BytesIO(file_content), 'test.zip')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Student not found', response.data)

    def test_submit_invalid_course(self):
        data = {
            'student_name': 's-nhohnn',
            'course_name': 'invalid_course'
        }
        file_content = b'This is a test zip file'
        data['submission'] = (BytesIO(file_content), 'test.zip')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Course not found', response.data)

    def test_submit_invalid_file_type(self):
        data = {
            'student_name': 's-nhohnn',
            'course_name': 'Programmieren III'
        }
        file_content = b'This is not a zip file'
        data['submission'] = (BytesIO(file_content), 'test.txt')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'File type not allowed', response.data)

    def test_submit_missing_file(self):
        data = {
            'student_name': 's-nhohnn',
            'course_name': 'Programmieren III'
        }

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file part', response.data)


if __name__ == '__main__':
    unittest.main()
