import logging

from fastapi import FastAPI, HTTPException, Request

from api.db_handler import initialize_db
from api.routes import student_router, teacher_router

app = FastAPI()
app.include_router(student_router)
app.include_router(teacher_router)
initialize_db()


@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("Content-Length")

    if content_length:
        content_length = int(content_length)
        if content_length > 50 * 1024 * 1024:  # 50 MB
            logging.warning("File upload rejected - size exceeds 50MB limit")
            raise HTTPException(status_code=413, detail="File too large (>50MB)")

    return await call_next(request)
