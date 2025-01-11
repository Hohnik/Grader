import pytest
from pathlib import Path
import tempfile
import shutil
import subprocess
from services.grader.main import ContainerGrader

@pytest.fixture
def sample_submission():
    """Create a temporary submission directory with a solution"""
    with tempfile.TemporaryDirectory() as temp_dir:
        submission_dir = Path(temp_dir) / "submission"
        src_dir = submission_dir / "src"
        src_dir.mkdir(parents=True)
        
        # Create a simple solution file
        (src_dir / "solution.py").write_text("""
def add(a, b):
    return a + b
""")
        
        yield submission_dir

@pytest.fixture
def sample_course():
    """Create a temporary course with tests and Dockerfile"""
    with tempfile.TemporaryDirectory() as temp_dir:
        course_dir = Path(temp_dir) / "course"
        course_dir.mkdir()
        
        # Create test file
        tests_dir = course_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_solution.py").write_text("""
def test_add():
    from src.solution import add
    assert add(2, 2) == 4
""")
        
        # Create Dockerfile
        (course_dir / "Dockerfile").write_text("""
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["pytest", "-v", "tests/"]
""")
        
        # Create requirements.txt
        (course_dir / "requirements.txt").write_text("pytest>=7.0.0")
        
        yield course_dir

def test_grader_creates_container(sample_submission, sample_course):
    """Test that grader creates and uses a container"""
    grader = ContainerGrader()
    result = grader.grade(sample_submission, sample_course)
    
    assert result.score is not None
    assert result.feedback is not None
    assert "test_add" in result.feedback
    # Container should be removed after grading
    containers = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=grader_"],
        capture_output=True, text=True
    )
    assert "grader_" not in containers.stdout

def test_grader_handles_failing_tests(sample_submission, sample_course):
    """Test that grader properly handles failing tests"""
    # Modify solution to be incorrect
    (sample_submission / "src" / "solution.py").write_text("""
def add(a, b):
    return a - b  # Wrong implementation
""")
    
    grader = ContainerGrader()
    result = grader.grade(sample_submission, sample_course)
    
    assert result.score == 0
    assert "FAILED" in result.feedback
    assert "AssertionError" in result.feedback

def test_grader_handles_syntax_error(sample_submission, sample_course):
    """Test that grader properly handles syntax errors"""
    # Create file with syntax error
    (sample_submission / "src" / "solution.py").write_text("""
def add(a, b)  # Missing colon
    return a + b
""")
    
    grader = ContainerGrader()
    result = grader.grade(sample_submission, sample_course)
    
    assert result.score == 0
    assert "SyntaxError" in result.feedback

def test_grader_cleans_up_on_error():
    """Test that grader cleans up containers even on errors"""
    grader = ContainerGrader()
    
    try:
        # Try to grade non-existent directories
        grader.grade(Path("/nonexistent"), Path("/nonexistent"))
    except Exception:
        pass
        
    # Check no containers are left
    containers = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=grader_"],
        capture_output=True, text=True
    )
    assert "grader_" not in containers.stdout 