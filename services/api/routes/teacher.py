import logging
import os
import zipfile

from fastapi import APIRouter, File, Form, UploadFile

from config import settings

router = APIRouter()

# TODO:
# Remove dockerfile, tests, requirements
# Remove directory creation
# Example_submission has to be uploaded
# Container_url has to be provided
# Add course to database
# Server has to run the process once to test
# Remove from database if not working
# -- Extras
# Set default value for start date
# Validate user with password and username
# Check if user wants to override existing courses


@router.post("/teacher/upload/")
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
    logging.info(
        f"Teacher upload received - Course: {course_name}, Teacher: {username}"
    )
    logging.debug(f"Course details - Start: {start_date}, End: {end_date}")

    course_dir = f"{settings.paths.courses_dir}/{course_name}"

    unzipped = zipfile.ZipFile(tests.file, "r")
    os.makedirs(f"{course_dir}/tests", exist_ok=True)
    unzipped.extractall(f"{course_dir}/tests/")

    with open(f"{course_dir}/dockerfile", "wb") as f:
        f.write(dockerfile.file.read())
    with open(f"{course_dir}/requirements.txt", "wb") as f:
        f.write(requirements.file.read())

    logging.info(f"Course files uploaded successfully - Course: {course_name}")
    logging.info("")
