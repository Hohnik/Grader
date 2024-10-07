import re
import os
import zipfile

ALLOWED_EXTENSIONS = {'zip'}

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

