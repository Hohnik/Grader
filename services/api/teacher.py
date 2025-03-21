import logging
import os
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from .db_handler import upsert_course_by_name
from .grader_handler import grade_submission

router = APIRouter()

# TODO:
# [ ] Validate user with password and username
# [ ] Set default value for start date
# [ ] Check if user wants to override existing courses


@router.post("/teacher/upload/")
async def teacher_upload(
    username: str = Form(None),
    password: str = Form(None),
    course_name: str = Form(None),
    container_name: str = Form(None),
    example_submission: UploadFile = File(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
):
    logging.info("Create/Update Course")
    score = None
    with tempfile.TemporaryDirectory(
        dir=Path(f"{os.path.dirname(__file__)}/_tmp/").resolve()
    ) as tempdir:
        tmp_path = Path(tempdir)
        zip_path = tmp_path / "src.zip"
        src_path = tmp_path / "src"
        output_path = tmp_path / "output"
        src_path.mkdir(parents=True, exist_ok=True)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(zip_path, "wb") as file:
            content = await example_submission.read()
            file.write(content)

        with zipfile.ZipFile(zip_path) as zip:
            zip.extractall(src_path)
            os.remove(zip_path)

        score_url = await grade_submission(tempdir, container_name)
        with open(score_url, "r") as file:
            score = file.read()

    if not score:
        return "Score is empty. Please update your tests."

    upsert_course_by_name(course_name, container_name)
    return score

    logging.info(f"Course files uploaded successfully - Course: {course_name}")
