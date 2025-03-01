from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.db_handler import fetch_all_courses, fetch_all_students

from .tags import a, div, h1, h2, html, li, table, tbody, td, th, tr, ul

router = APIRouter()

styles = """
    <style>
        /* General Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            background-color: #f5f7f9;
            color: #333;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        h1 {
            font-size: 28px;
            margin-bottom: 25px;
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }

        h2 {
            font-size: 22px;
            margin: 20px 0 15px 0;
            color: #3498db;
        }

        /* Table Styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            box-shadow: 0 2px 3px rgba(0, 0, 0, 0.05);
        }

        th {
            background-color: #3498db;
            color: white;
            font-weight: 600;
            text-align: left;
            padding: 12px 15px;
        }

        td {
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }

        tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        tr:hover {
            background-color: #f1f4f7;
        }

        /* Keep the original list styling for fallback */
        ul {
            list-style-type: none;
            padding: 0;
            margin-bottom: 20px;
        }

        li {
            margin-bottom: 10px;
            padding: 10px;
            background: #f1f1f1;
            border-radius: 4px;
        }

        /* Link styling - works for both table links and list links */
        a {
            color: #3498db;
            text-decoration: none;
            transition: color 0.2s;
        }

        a:hover {
            color: #2980b9;
            text-decoration: underline;
        }

        footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #7f8c8d;
        }

        /* Add a bit of responsiveness for smaller screens */
        @media (max-width: 600px) {
            .container {
                padding: 15px;
            }
            
            th, td {
                padding: 8px 10px;
            }
            
            h1 {
                font-size: 24px;
            }
            
            h2 {
                font-size: 20px;
            }
        }
    </style>
    """

@router.get("/", response_class=HTMLResponse)
def root():
    fetched_students = fetch_all_students()
    fetched_courses = fetch_all_courses()
    print(fetched_courses)
    print(fetched_students)

    if fetched_students:
        students = table(
            tr(th("ID"), th("Username")),
            "".join(
                tr(td(str(id)), td(username))
                for (id, username) in fetched_students
            )
        )
    else:
        students = ul(li("No students found"))

    if fetched_courses:
        courses = table(
            tr(
                th("ID"),
                th("Name"),
                th("Repository")
            ),
            "".join(
                tr(
                    td(str(id)),
                    td(coursename),
    td(a(f"{containerUrl}", href=f"https://hub.docker.com/repository/docker/{containerUrl.split(':')[0]}/general", target="_blank"))
                )
                for (id, coursename, containerUrl) in fetched_courses
                )
        )
    else:
        courses = ul(li("No courses available"))

    return html(
        div(
            h1("Students and Courses"),
            h2("Students"),
            students,
            h2("Courses"),
            courses,
            classes=["container"],
        ),
        head_content="",
        styles=styles
    )


