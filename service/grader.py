import logging
import zipfile

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from container.utils import spawn_container
from utils import course_ok, save_submission, student_ok

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
    if not course_ok(course_name):
        raise HTTPException(
            status_code=400, detail="Course not found. Check for spelling errors!"
        )

    if not student_ok(student_name):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    if not zipfile.is_zipfile(submission.file):
        raise HTTPException(
            status_code=415, detail="Filetype not allowed. Only '*.zip' files"
        )

    sub_id: int = save_submission(student_name, course_name, submission)
    logging.info(f"{sub_id}:{course_name}/{student_name} - submission saved")

    score: str = await spawn_container(sub_id, student_name, course_name)

    with open(f"submissions/{course_name}/{student_name}/score.txt", "a") as f:
        f.write(score)
    logging.info(f"{sub_id}:{course_name}/{student_name} - score:{score}")

    return JSONResponse(
        {
            "message": f"Submission with ID {id} successful",
            "submission_number": sub_id,
            "score": score,
        },
        status_code=200,
    )


# @app.post("/upload")
# async def lecturer_upload(
#     submission: UploadFile = File(None),
#     lecturer_name: str = Form(None),
#     course_name: str = Form(None),
#     start_date: str = Form(None),
#     end_date: str = Form(None),
# ):
#     if not course_ok(course_name):  # not empty, characters, in db
#         raise HTTPException(
#             status_code=400, detail="Course not found. Check for spelling errors!"
#         )
#     if not student_ok(course_name):  # not empty, characters, in db
#         raise HTTPException(
#             status_code=400, detail="Course not found. Check for spelling errors!"
#         )
#
#     if not student_ok(lecturer_name):  # not empty, characters, in db
#         raise HTTPException(status_code=401, detail="Unauthorized user")
#
#     # Create the directory for storing the Dockerfile
#
#     # Save the Dockerfile
