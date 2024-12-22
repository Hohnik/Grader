import logging
import os
import shutil
import zipfile

from db.utils import next_id
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from container.utils import spawn_container
from utils import course_ok, student_ok

app = FastAPI()
logging.basicConfig(filename="grader.log", level=logging.INFO)


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("Content-Length")

    if content_length:
        content_length = int(content_length)
        if content_length > 50 * 1024 * 1024:  # 50 MB
            raise HTTPException(status_code=413, detail=f"File to large. (>50mb)")

    return await call_next(request)


@app.post("/submit")
async def submit(
    submission: UploadFile = File(),
    student_name: str = Form(),
    course_name: str = Form(),
):
    logging.info(f"{course_name}:{student_name} - submission received")

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

    course_dir = f"courses/{course_name}"
    student_dir = f"submissions/{course_name}/{student_name}"

    tests_dir = f"{course_dir}/tests"
    dockerfile = f"{course_dir}/Dockerfile"
    shutil.copytree(
        tests_dir, f"submissions/{course_name}/{student_name}/tests", dirs_exist_ok=True
    )
    shutil.copy(dockerfile, f"submissions/{course_name}/{student_name}/Dockerfile")

    os.makedirs(student_dir, exist_ok=True)
    zip_url = f"submissions/{course_name}/{student_name}/{task_id}.zip"
    with open(zip_url, "wb") as f:
        f.write(submission.file.read())

    with zipfile.ZipFile(zip_url, "r") as zip_ref:
        zip_ref.extractall(f"{student_dir}/src/")

    score_url = await spawn_container(task_id, student_dir)
    logging.info(f"{task_id}:{student_dir} - score:{score_url}")

    score = None
    with open(score_url, "r") as f:
        score = f.read()

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
):
    logging.info(f"{username}:{password}:{course_name}:{start_date}:{end_date}")

    unzipped = zipfile.ZipFile(tests.file, "r")
    os.makedirs(f"courses/{course_name}/tests", exist_ok=True)
    unzipped.extractall(f"courses/{course_name}/tests/")

    with open(f"courses/{course_name}/dockerfile", "wb") as f:
        f.write(dockerfile.file.read())
