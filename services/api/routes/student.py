import logging
import os
import shutil
from io import BytesIO
from zipfile import ZipFile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.db_handler import submission_id
from api.grader_handler import grade_submission
from config import settings
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
    logging.info("-")
    logging.info(
        f"Submission received - Course: {course_name}, Student: {student_name}"
    )

    # Get submission ID
    sub_id = submission_id()
    assert sub_id is not None
    logging.info(f"Submission ID: {sub_id}")

    # Create submission directory
    course_dir = f"{settings.paths.courses_dir}/{course_name}"
    submission_dir = (
        f"{settings.paths.submissions_dir}/{course_name}/{student_name}/{sub_id}"
    )
    os.makedirs(submission_dir, exist_ok=True)
    logging.info(f"Created submission directory: {submission_dir}")
    with ZipFile(BytesIO(submission.file.read())) as zip_ref:
        zip_ref.extractall(submission_dir)
    logging.info(f"Unziped src/")

    # Copy course files to submission directory
    shutil.copytree(f"{course_dir}/tests", f"{submission_dir}/tests")
    shutil.copy(f"{course_dir}/Dockerfile", f"{submission_dir}/Dockerfile")
    shutil.copy(f"{course_dir}/requirements.txt", f"{submission_dir}/requirements.txt")
    logging.info("Copied course files to submission directory")

    logging.info(f"Start grading")
    score = await grade_submission(submission_dir)

    # Clean up all temporary files after grading
    cleanup_student_directory(submission_dir)

    logging.info(f"Grading completed for ID: {sub_id}, Score: {score}")

    return JSONResponse(
        {
            "score": score,
        },
        status_code=200,
    )
