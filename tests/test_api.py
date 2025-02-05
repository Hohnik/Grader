import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import zipfile
import tempfile
import shutil
from services.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and cleanup after each test"""
    # Setup
    data_dir = Path("data")
    if data_dir.exists():
        shutil.rmtree(data_dir)

    yield

    # Cleanup
    if data_dir.exists():
        shutil.rmtree(data_dir)


@pytest.fixture
def correct_solution_zip():
    """Create a zip file with a correct solution"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file, "w") as zip_ref:
            zip_ref.writestr(
                "solution.py",
                """
def add(a, b):
    return a + b
            """,
            )
        return tmp_file.name


@pytest.fixture
def incorrect_solution_zip():
    """Create a zip file with an incorrect solution"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file, "w") as zip_ref:
            zip_ref.writestr(
                "solution.py",
                """
def add(a, b):
    return a - b  # Wrong implementation!
            """,
            )
        return tmp_file.name


@pytest.fixture
def syntax_error_solution_zip():
    """Create a zip file with a syntax error"""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        with zipfile.ZipFile(tmp_file, "w") as zip_ref:
            zip_ref.writestr(
                "solution.py",
                """
def add(a, b)
    return a + b  # Missing colon!
            """,
            )
        return tmp_file.name


@pytest.fixture
def sample_course():
    """Create a sample course with actual tests"""
    course_dir = Path("data/courses/test-course")
    course_dir.mkdir(parents=True, exist_ok=True)

    tests_dir = course_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Create multiple test cases
    (tests_dir / "test_solution.py").write_text("""
import pytest
from src.solution import add

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 5) == 5
""")

    return "test-course"


def test_correct_solution_gets_full_score(correct_solution_zip, sample_course):
    """Test that a correct solution gets full score"""
    with open(correct_solution_zip, "rb") as f:
        response = client.post(
            "/student/submit",
            files={"submission": ("solution.zip", f, "application/zip")},
            data={"student_name": "test_student", "course_name": sample_course},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 100
    assert "All tests passed!" in result["feedback"]
    assert "test_add_positive" in result["feedback"]
    assert "FAILED" not in result["feedback"]


def test_incorrect_solution_fails_tests(incorrect_solution_zip, sample_course):
    """Test that an incorrect solution fails tests"""
    with open(incorrect_solution_zip, "rb") as f:
        response = client.post(
            "/student/submit",
            files={"submission": ("solution.zip", f, "application/zip")},
            data={"student_name": "test_student", "course_name": sample_course},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["score"] < 100
    assert "Some tests failed" in result["feedback"]
    assert "FAILED" in result["feedback"]
    assert "assert" in result["feedback"]  # Should show assertion error


def test_syntax_error_in_solution(syntax_error_solution_zip, sample_course):
    """Test handling of syntax errors in submitted code"""
    with open(syntax_error_solution_zip, "rb") as f:
        response = client.post(
            "/student/submit",
            files={"submission": ("solution.zip", f, "application/zip")},
            data={"student_name": "test_student", "course_name": sample_course},
        )

    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 0
    assert "SyntaxError" in result["feedback"]


def test_submit_invalid_file_type(sample_course):
    """Test submitting a non-zip file"""
    response = client.post(
        "/student/submit",
        files={"submission": ("solution.txt", b"not a zip", "text/plain")},
        data={"student_name": "test_student", "course_name": sample_course},
    )

    assert response.status_code == 415
    assert "Invalid file type" in response.json()["detail"]


def test_submit_nonexistent_course(correct_solution_zip):
    """Test submitting to a course that doesn't exist"""
    with open(correct_solution_zip, "rb") as f:
        response = client.post(
            "/student/submit",
            files={"submission": ("solution.zip", f, "application/zip")},
            data={"student_name": "test_student", "course_name": "nonexistent-course"},
        )

    assert response.status_code == 404
    assert "Course nonexistent-course not found" in response.json()["detail"]
