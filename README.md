# Automated Python Grading System

A containerized grading system for Python assignments that provides automated testing and scoring. The system supports weighted tests and maintains a history of student submissions.

## For Server Administrators

### System Requirements
- Python 3.11+
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
uv pip install .
```

4. Start the grading service:
```bash
uvicorn grader:app --host 0.0.0.0 --port 8000
```

### Configuration
- Ensure Docker is installed and running
- The service stores submissions in `service/submissions/<course>/<student>/<submission_id>/`
- Course files are stored in `service/courses/<course_name>/`
- Logs are written to `service/grader.log`

## For Teachers

### Creating a New Course

1. Edit the `config.yaml` in your course directory:
```yaml
course_name: "Programmieren"
server_url: "http://localhost:8000"
```

2. Prepare your test files in the `tests/` directory. Tests can be weighted using `@pytest.mark.weight(n)`.

Example test file:
```python
from src.main import *

@pytest.mark.weight(2)  # This test is worth 2 points
def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

def test_basic():  # Default weight is 1 point
    assert multiply(2, 3) == 6
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
python submit.py
```

### Scoring
- Each test has a weight (default: 1)
- Final score is calculated as: (passed_weight / total_weight) * 100
- Detailed test output is provided in the response
- All submission attempts are preserved in `submissions/<course>/<student>/<id>/`
