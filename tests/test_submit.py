import pytest
import os
from pathlib import Path
import yaml
import respx
import httpx
from client.submit import load_config, submit_assignment

@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file for testing"""
    config_path = tmp_path / "config.yaml"
    config_data = {
        "student_name": "Test Student",
        "course_name": "test-course",
        "server_url": "http://localhost:8000"
    }
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return config_path

@pytest.fixture
def temp_src_dir(tmp_path):
    """Create a temporary src directory with a dummy file"""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "solution.py").write_text("def solve(): return 42")
    return src_dir

@pytest.fixture
def mock_successful_submission():
    """Mock a successful submission response"""
    with respx.mock() as mock:
        mock.post("http://localhost:8000/student/submit").respond(
            status_code=200,
            json={"score": 100, "feedback": "Great work!"}
        )
        yield mock

@pytest.fixture
def mock_failed_submission():
    """Mock a failed submission response"""
    with respx.mock() as mock:
        mock.post("http://localhost:8000/student/submit").respond(
            status_code=400,
            json={"error": "Invalid submission"}
        )
        yield mock

def test_load_config_success(temp_config):
    """Test successful config loading"""
    config = load_config(str(temp_config))
    assert config["student_name"] == "Test Student"
    assert config["course_name"] == "test-course"
    assert config["server_url"] == "http://localhost:8000"

def test_load_config_file_not_found():
    """Test config loading with non-existent file"""
    with pytest.raises(SystemExit):
        load_config("nonexistent.yaml")

def test_load_config_invalid_yaml(tmp_path):
    """Test config loading with invalid YAML"""
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("invalid: yaml: content")
    with pytest.raises(SystemExit):
        load_config(str(config_path))

def test_submit_assignment_missing_src_dir(temp_config):
    """Test submission with missing src directory"""
    config = load_config(str(temp_config))
    with pytest.raises(SystemExit):
        submit_assignment(config, Path("nonexistent_src")) 

def test_successful_submission(temp_config, temp_src_dir, mock_successful_submission):
    """Test a successful submission process"""
    config = load_config(str(temp_config))
    result = submit_assignment(config, temp_src_dir)
    
    assert result["score"] == 100
    assert result["feedback"] == "Great work!"
    assert mock_successful_submission.calls.last.request.method == "POST"
    
    # Verify the zip file was cleaned up
    assert not Path("submission.zip").exists()

def test_failed_submission(temp_config, temp_src_dir, mock_failed_submission):
    """Test handling of a failed submission"""
    config = load_config(str(temp_config))
    
    with pytest.raises(SystemExit):
        submit_assignment(config, temp_src_dir)
    
    # Verify the zip file was cleaned up even after failure
    assert not Path("submission.zip").exists() 