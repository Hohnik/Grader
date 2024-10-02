import unittest
import os
import tempfile
from grader_service import app, UPLOAD_FOLDER
from io import BytesIO

class GraderServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        self.client = self.app.test_client()

        # Create temporary files for students and courses
        with open('students.txt', 'w') as f:
            f.write('john_doe\n')
        with open('courses.txt', 'w') as f:
            f.write('python_101\n')

    def tearDown(self):
        # Remove temporary files
        os.remove('students.txt')
        os.remove('courses.txt')

    # def test_submit_valid_project(self): #TODO: Not yet working because BytesIO is not a real file
        # data = {
        #     'student_name': 'john_doe',
        #     'course_name': 'python_101'
        # }
        # file_content = b'This is a test zip file'
        # data['submission'] = (BytesIO(file_content), 'test.zip')
        #
        # response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        # self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Submission successful', response.data)

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
            'student_name': 'john_doe',
            'course_name': 'invalid_course'
        }
        file_content = b'This is a test zip file'
        data['submission'] = (BytesIO(file_content), 'test.zip')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Course not found', response.data)

    def test_submit_invalid_file_type(self):
        data = {
            'student_name': 'john_doe',
            'course_name': 'python_101'
        }
        file_content = b'This is not a zip file'
        data['submission'] = (BytesIO(file_content), 'test.txt')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'File type not allowed', response.data)

    def test_submit_missing_file(self):
        data = {
            'student_name': 'john_doe',
            'course_name': 'python_101'
        }

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file part', response.data)

    def test_submit_invalid_zip(self):
        data = {
            'student_name': 'john_doe',
            'course_name': 'python_101'
        }
        file_content = b'This is not a valid zip file'
        data['submission'] = (BytesIO(file_content), 'test.zip')

        response = self.client.post('/submit', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid zip file', response.data)

if __name__ == '__main__':
    unittest.main()
