import logging
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.db_handler import get_container_by_course_name, get_submission_id
from api.grader_handler import grade_submission
from config import settings


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

    # TODO: validate if course exists (also student_name?)

    id = get_submission_id()
    sub_dir = create_submission_dir(id, submission, student_name, course_name)
    score_url = await grade_submission(sub_dir, get_container_by_course_name(course_name))
    score = None
    with open(score_url, "r") as file:
        score = file.read()

    logging.info(f"Grading completed for ID: {id}, Score: {score}")
    return JSONResponse(
        {
            "score": score,
        },
        status_code=200,
    )


def create_submission_dir(id, submission, student, course):
    """
    Creates a directory e.g.
    _submissions/
        Programmieren1/
            s-nhohnn/
                id37/
                    src/
                        main.py
    """
    sub_dir = f"{settings.paths.submissions_dir}/{course}/{student}/id{id}"
    base_path = Path(sub_dir).resolve()
    src_path = base_path / "src"
    output_path = base_path / "output"

    src_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    with ZipFile(BytesIO(submission.file.read())) as zip_ref:
        zip_ref.extractall(src_path)
    logging.info("Unziped submission")

    return sub_dir
