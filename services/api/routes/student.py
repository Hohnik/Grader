import logging
import os
import shutil
import zipfile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.db_handler import submission_id
from grader.grader import spawn_container
from utils import cleanup_student_directory


class submission(BaseModel):
    username: str
    submission: str


router = APIRouter()


@router.post("/student/submit/")
async def submit(
    submission: UploadFile = File(),
    student_name: str = Form(),
    course_name: str = Form(),
):
    logging.info(
        f"Student submission received - Course: {course_name}, Student: {student_name}"
    )

    task_id = submission_id()
    assert task_id is not None
    logging.info(f"Generated task ID: {task_id}")

    course_dir = f"courses/{course_name}"
    student_base_dir = f"submissions/{course_name}/{student_name}"
    submission_dir = (
        f"{student_base_dir}/{task_id}"  # Create specific directory for this submission
    )

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
    logging.debug("Copied course files to submission directory")

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
            if (
                file_name.endswith("/")
                or file_name.startswith("__")
                or file_name.startswith(".")
            ):
                continue

            # Extract the file to src directory
            zip_info = zip_ref.getinfo(file_name)
            zip_info.filename = os.path.basename(
                file_name
            )  # Remove any path components
            zip_ref.extract(zip_info, f"{submission_dir}/src")

    logging.debug("Extracted submission files to src directory")

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
            "message": "Submission successful",
            "submission_number": task_id,
            "score": score,
        },
        status_code=200,
    )
