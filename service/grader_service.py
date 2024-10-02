import os
import re
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import zipfile
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configuration
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
UPLOAD_FOLDER = 'submissions'
ALLOWED_EXTENSIONS = {'zip'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['TESTING'] = False

# Setup logging
logging.basicConfig(filename='grader_service.log', level=logging.INFO)

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute", "100 per day"]
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_name(name):
    return re.match(r'^[a-zA-Z0-9_\-\. ]+$', name) is not None

def check_name_in_file(name, filename):
    with open(filename, 'r') as f:
        return name in [line.strip() for line in f]

def get_next_submission_number(directory):
    existing_files = [f for f in os.listdir(directory) if f.endswith('.zip')]
    return len(existing_files) + 1

def is_valid_zip(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            return True
    except zipfile.BadZipFile:
        return False

@app.route('/submit', methods=['POST'])
@limiter.limit("1 per minute", exempt_when=lambda: app.config['TESTING'])  # Limit submissions to 1 per minute per user, except when testing
def submit_project():
    if 'submission' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['submission']
    student_name = request.form.get('student_name')
    course_name = request.form.get('course_name')
    logging.info(f"{student_name}, {course_name}")

    if not all([file, student_name, course_name]):
        return jsonify({"error": "Missing required information"}), 400

    if not validate_name(student_name) or not validate_name(course_name):
        return jsonify({"error": "Invalid student or course name"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Check if student and course are valid
    if not check_name_in_file(student_name, 'students.txt'):
        return jsonify({"error": "Student not found"}), 400
    if not check_name_in_file(course_name, 'courses.txt'):
        return jsonify({"error": "Course not found"}), 400

    # Create directory structure
    submission_dir = os.path.join(app.config['UPLOAD_FOLDER'], course_name, student_name)
    os.makedirs(submission_dir, exist_ok=True)

    # Save the file with an ongoing number
    submission_number = get_next_submission_number(submission_dir)
    filename = secure_filename(f"{submission_number}.zip")
    filepath = os.path.join(submission_dir, filename)
    file.save(filepath)

    # Validate zip file
    if not is_valid_zip(filepath):
        os.remove(filepath)
        return jsonify({"error": "Invalid zip file"}), 400

    # Log the successful submission
    logging.info(f"Successful submission: {student_name} - {course_name} - {filename}")

    return jsonify({"message": "Submission successful", "submission_number": submission_number}), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File size exceeds 50MB limit"}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded"}), 429

if __name__ == '__main__':
    app.run(debug=False)  # Set to False in production
