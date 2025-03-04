# Automated Python Grading System

A containerized grading system for Python(for now) assignments that provides automated testing and scoring. The system supports weighted tests and maintains a history of student submissions.

## For Server Administrators

### System Requirements
- Python 3.12+
- Docker Desktop (for macOS/Windows) or Docker Engine (for Linux)
- uv (for dependency management)

### Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd grader
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install uv and dependencies:
```bash
pip install uv
cd service
uv sync
```

4. Start the grading service:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Configuration
- Ensure Docker is installed and running
- The service stores submissions in `service/_submissions/<course>/<student>/<submission_id>/`
- Logs are written to `service/grader.log`

## For Teachers
### Creating a New Course

1. Create a container and upload it to dockerhub. 
    - It has to contain a `/app/src/` and `/app/output/` directory. These will get mounted to the server.
    - The students code is mounted to `/app/src/` and the score needs to be written to `/app/output/score.txt`
```python
# TODO: Example here
```


2. Edit the `config.yaml` in your course directory:
```yaml
username: example_username
password: example_password

course_name: example_course
container_name: example_user/example_repo:latest # TODO: Check if it is possible to make this a full URL

start_date: 02.12.2024
end_date: 30.12.2024
```

3. Run the upload script:
```bash
python submit_prof.py
```

## For Students

### Submitting Assignments

1. Edit your `config.yaml`:
```yaml
student_name: "s-username"
course_name: "Programmieren"
server_url: "http://localhost:8000"
```

2. Create your solution in `src/main.py`:
```python
# src/main.py
def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
```

3. Submit your solution:
```bash
python submit_stud.py
```
