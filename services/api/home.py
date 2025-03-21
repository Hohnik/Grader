from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .db_handler import (
    add_student_by_name,
    delete_course_by_id,
    delete_student_by_id,
    fetch_courses,
    fetch_students,
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/students", response_class=HTMLResponse)
async def get_students():
    fetched_students = fetch_students()
    if fetched_students:
        students_html = "".join(
            f"""
            <tr>
                <td>{id}</td>
                <td>{username}</td>
                <td style="color: #F00; text-align: center">
                    <button class="btn-delete" 
                        hx-delete="/students/delete/{id}" 
                        hx-target="closest tr" 
                        hx-swap="outerHTML">X</button>
                </td>
            </tr>
            """
            for id, username in fetched_students
        )
        return f"""
        <table>
            <tr><th>ID</th><th>Username</th><th style="text-align: center;">Delete</th></tr>
            {students_html}
        </table>
        """
    else:
        return "<ul><li>No students found</li></ul>"


@router.post("/students/add", response_class=HTMLResponse)
def add_student(username: str = Form(None)):
    add_student_by_name(username)
    fetched_students = fetch_students()
    fetched_students = fetch_students()
    students_html = "".join(
        f"""
        <tr>
            <td>{id}</td>
            <td>{username}</td>
            <td style="color: #F00; text-align: center">
                <button class="btn-delete" 
                    hx-delete="/students/delete/{id}" 
                    hx-target="closest tr" 
                    hx-swap="outerHTML">X</button>
            </td>
        </tr>
        """
        for id, username in fetched_students
    )
    return f"""
    <table>
        <tr><th>ID</th><th>Username</th><th style="text-align: center;">Delete</th></tr>
        {students_html}
    </table> 
    """


@router.delete("/students/delete/{id}")
async def delete_student(id: int):
    res = delete_student_by_id(id)
    if res:
        return Response(status_code=200, content="")
    else:
        return JSONResponse({"error": "Student not fount"}, status_code=404)


@router.get("/courses", response_class=HTMLResponse)
async def get_courses():
    fetched_courses = fetch_courses()
    if fetched_courses:
        courses_html = "".join(
            f"""
            <tr id="row_{id}">
                <td>{id}</td>
                <td>{coursename}</td>
                <td><a href="https://hub.docker.com/repository/docker/{containerUrl.split(':')[0]}/general" target="_blank">{containerUrl}</a></td>
                <td style="color: #F00; text-align: center">
                <button class="btn-delete" 
                    hx-delete="/courses/delete/{id}" 
                    hx-target="closest tr" 
                    hx-swap="outerHTML">X</button>
                </td>
            </tr>
            """
            for id, coursename, containerUrl in fetched_courses
        )
        return f"""
        <table >
            <tr><th>ID</th><th>Name</th><th>Repository</th><th style="text-align: center;">Delete</th></tr>
            {courses_html}
        </table>
        """
    else:
        return "<ul><li>No courses available</li></ul>"


@router.delete("/courses/delete/{id}")
async def delete_course(id: int):
    res = delete_course_by_id(id)
    if res:
        return Response(status_code=200, content="")
    else:
        return JSONResponse({"error": "Course not fount"}, status_code=404)
