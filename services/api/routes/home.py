from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from api.db_handler import delete_course_by_id, fetch_courses, fetch_students

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
            f"<tr><td>{id}</td><td>{username}</td></tr>"
            for id, username in fetched_students
        )
        return f"""
        <table>
            <tr><th>ID</th><th>Username</th></tr>
            {students_html}
        </table>
        """
    else:
        return "<ul><li>No students found</li></ul>"


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
            <tr><th>ID</th><th>Name</th><th>Repository</th><th>Delete</th></tr>
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
