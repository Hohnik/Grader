import re
import os
import zipfile


def is_zip():
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["zip"]

def is_valid_zip(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            return True
    except zipfile.BadZipFile:
        return False

def is_valid_name(name):
    return re.match(r'^[a-zA-Z0-9_\-\. ]+$', name) is not None

def name_in_db(name, filename):
    with open(filename, 'r') as f:
        return name in [line.strip() for line in f]

def next_file_name(directory):
    existing_files = [f for f in os.listdir(directory) if f.endswith('.zip')]
    return len(existing_files) + 1


