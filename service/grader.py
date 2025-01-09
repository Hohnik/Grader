import logging
import os
import shutil
import zipfile

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from container.utils import spawn_container, cleanup_student_directory
from db.utils import next_id
from utils import course_ok, student_ok

app = FastAPI()
# Configure logging with a consistent format
logging.basicConfig(
    filename="grader.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("Content-Length")

    if content_length:
        content_length = int(content_length)
        if content_length > 50 * 1024 * 1024:  # 50 MB
            logging.warning(f"File upload rejected - size exceeds 50MB limit")
            raise HTTPException(status_code=413, detail=f"File too large (>50MB)")

    return await call_next(request)


@app.post("/submit")
async def submit(
    submission: UploadFile = File(),
    student_name: str = Form(),
    course_name: str = Form(),
):
    logging.info(f"Student submission received - Course: {course_name}, Student: {student_name}")

    # if not course_ok(course_name):
    #     raise HTTPException(
    #         status_code=400, detail="Course not found. Check for spelling errors!"
    #     )
    #
    # if not student_ok(student_name):
    #     raise HTTPException(status_code=401, detail="Unauthorized user")
    #
    # if not zipfile.is_zipfile(submission.file):
    #     raise HTTPException(
    #         status_code=415, detail="Filetype not allowed. Only '*.zip' files"
    #     )

    task_id = next_id()
    assert task_id is not None
    logging.info(f"Generated task ID: {task_id}")

    course_dir = f"courses/{course_name}"
    student_base_dir = f"submissions/{course_name}/{student_name}"
    submission_dir = f"{student_base_dir}/{task_id}"  # Create specific directory for this submission

    # Create directories
    os.makedirs(student_base_dir, exist_ok=True)
    os.makedirs(submission_dir, exist_ok=True)
    logging.debug(f"Created submission directory: {submission_dir}")

    # Copy course files to submission directory
    tests_dir = f"{course_dir}/tests"
    dockerfile = f"{course_dir}/Dockerfile"
    requirements = f"{course_dir}/requirements.txt"
    shutil.copytree(tests_dir, f"{submission_dir}/tests", dirs_exist_ok=True)
    shutil.copy(dockerfile, f"{submission_dir}/Dockerfile")
    shutil.copy(requirements, f"{submission_dir}/requirements.txt")
    logging.debug(f"Copied course files to submission directory")

    # Save and extract the submission
    zip_url = f"{submission_dir}/{task_id}.zip"
    with open(zip_url, "wb") as f:
        f.write(submission.file.read())

    # Create src directory
    os.makedirs(f"{submission_dir}/src", exist_ok=True)
    
    # Extract submission to src directory
    with zipfile.ZipFile(zip_url, "r") as zip_ref:
        # List all files in the zip
        file_list = zip_ref.namelist()
        
        for file_name in file_list:
            # Skip directories and hidden files
            if file_name.endswith('/') or file_name.startswith('__') or file_name.startswith('.'):
                continue
                
            # Extract the file to src directory
            zip_info = zip_ref.getinfo(file_name)
            zip_info.filename = os.path.basename(file_name)  # Remove any path components
            zip_ref.extract(zip_info, f"{submission_dir}/src")
    
    logging.debug(f"Extracted submission files to src directory")

    score_url = await spawn_container(task_id, submission_dir)
    score = None
    with open(score_url, "r") as f:
        score = f.read()
    
    # Clean up all temporary files after grading
    cleanup_student_directory(submission_dir)
    
    logging.info(f"Grading completed - Task: {task_id}, Score: {score}")
    logging.info("")  # Add blank line after submission

    return JSONResponse(
        {
            "message": f"Submission successful",
            "submission_number": task_id,
            "score": score,
        },
        status_code=200,
    )


@app.post("/upload")
async def teacher_upload(
    username: str = Form(None),
    password: str = Form(None),
    course_name: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
    tests: UploadFile = File(None),
    dockerfile: UploadFile = File(None),
    requirements: UploadFile = File(None),
):
    logging.info(f"Teacher upload received - Course: {course_name}, Teacher: {username}")
    logging.debug(f"Course details - Start: {start_date}, End: {end_date}")

    course_dir = f"courses/{course_name}"

    unzipped = zipfile.ZipFile(tests.file, "r")
    os.makedirs(f"{course_dir}/tests", exist_ok=True)
    unzipped.extractall(f"{course_dir}/tests/")

    with open(f"{course_dir}/dockerfile", "wb") as f:
        f.write(dockerfile.file.read())
    with open(f"{course_dir}/requirements.txt", "wb") as f:
        f.write(requirements.file.read())
    
    logging.info(f"Course files uploaded successfully - Course: {course_name}")
    logging.info("")  # Add blank line after upload
