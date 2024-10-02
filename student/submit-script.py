import os
import yaml
import zipfile
import requests

def read_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def zip_src_directory():
    with zipfile.ZipFile('submission.zip', 'w') as zipf:
        for root, dirs, files in os.walk('src'):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), 'src'))

def submit_project(config):
    url = "http://127.0.0.1:5000/submit"  #TODO: Relace with real url
    
    files = {'submission': open('submission.zip', 'rb')}
    data = {
        'course_name': config['course_name'],
        'student_name': config['student_name']
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        print("Submission successful!")
    else:
        print(f"Submission failed with {response.status_code}: \
            \nMessage: {response.text}")

def main():
    config = read_config()
    zip_src_directory()
    submit_project(config)
    os.remove('submission.zip')  # Clean up the zip file after submission

if __name__ == "__main__":
    main()
