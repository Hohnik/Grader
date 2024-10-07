import os
import logging
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename

from utils import * 

app = FastAPI()

UPLOAD_FOLDER = 'submissions'
CONTAINER_FOLDER = 'container'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

logging.basicConfig(filename='grader_service.log', level=logging.INFO)

@app.post("/submit")
async def submit(
    submission: UploadFile = File(...),
    student_name: str = Form(...),
    course_name: str = Form(...)
):
    if not filesize_ok(submission): # zip, <= 50mb
        raise HTTPException(status_code=400, detail="Invalid zip file")


    validate_name(student_name) # not empty, characters, in db
    validate_course(course_name)

    safe_submission(student_name, submission) # create dir, generate filename
    validate_filetype(submission) # zip, <= 50mb
    log_success_message() # log and print first update
    return_success() # log and print first update


    # Log the successful submission
    logging.info(f"Successful submission: {student_name} - {course_name} - {filename}")

    return JSONResponse({"message": "Submission successful", "submission_number": submission_number}, status_code=200)


# Error handler for large file uploads
@app.exception_handler(413)
async def request_entity_too_large_handler(request, exc):
    return JSONResponse(status_code=413, content={"error": "File size exceeds 50MB limit"})

# raise HTTPException(status_code=400, detail="Invalid zip file")

# Route for lecturer upload (e.g., uploading Dockerfiles)
@app.post("/upload")
async def lecturer_upload(
    submission: UploadFile = File(None),
    lecturer_name: str = Form(None),
    course_name: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None)
):
    # Validate lecturer and course names

    # Check if lecturer and course are valid


    # Create the directory for storing the Dockerfile

    # Save the Dockerfile

# Error handler for handling general file size limits (optional)
@app.exception_handler(413)
async def request_entity_too_large_handler(request, exc):
    return JSONResponse({"error": "File size exceeds the limit"}, status_code=413)


