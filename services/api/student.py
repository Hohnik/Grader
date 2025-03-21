import logging
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from config import settings
from mail import send_mail_to

from .db_handler import create_submission, get_course_by_name, update_submission
from .grader_handler import grade_submission

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

    if not get_course_by_name(course_name):
        logging.info(f"Course '{course_name}' not found")
        return JSONResponse(
            content={"message": f"Course '{course_name}' not found."},
            status_code=200,
        )

    # TODO: validate if student exists

    id = create_submission()
    sub_dir = create_submission_dir(id, submission, student_name, course_name)
    container_url = get_course_by_name(course_name)[2]
    score_url = await grade_submission(sub_dir, container_url)
    score = None
    with open(score_url, "r") as file:
        score = file.read()

    update_submission(score)

    email = f"{student_name}@haw-landshut.de"
    subject = f"Submission {id} score"
    message = "This is a example message"  # TODO: Make up what message should be added
    send_mail_to(email, subject, message)

    logging.info(f"Grading completed for ID: {id}, Score: {score}")
    return JSONResponse(
        {
            "message": score,
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
