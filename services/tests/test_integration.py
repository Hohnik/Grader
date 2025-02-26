import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import docker
import requests
from dotenv import load_dotenv

load_dotenv()

def test_docker_running():
    client = docker.from_env()
    assert client.ping(), "Docker is not running!"


def test_create_image():
    client = docker.from_env()
    img = None
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            img = create_image(tmpdir)
            assert img in client.images.list(), "Image not found in image list"

    finally:
        if img:
            client.images.remove(img.id)

def test_upload_image():
    client = docker.from_env()
    img = None
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            img = create_image(tmpdir)
            upload_image(img)

    finally:
        if img:
            client.images.remove(img.id)


def test_submit():
    client = docker.from_env()
    image = None

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            src_dir_path = create_src_directory(tmpdir)
            zip_path = shutil.make_archive(src_dir_path,"zip",src_dir_path)
            image = create_image(tmpdir)
            repo_url = upload_image(image)

            url = "http://localhost:8000/teacher/upload"
            data = {
                "username": "test_user",
                "password": "test_password",
                "course_name": "test_course",
                "container_name": repo_url,
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(minutes=10)
            }
            files = {"example_submission": open(zip_path, "rb")}
            response = requests.post(url, data, files=files)

            assert response.status_code == 200

    finally:
        if image:
            client.images.remove(image.id)

# ----------------------------------------------------

def create_src_directory(directory: Path):
    src_dir = directory / "src"
    src_dir.mkdir()
    python_file = create_python_file(src_dir)

    assert src_dir.is_dir()
    assert python_file.name in os.listdir(src_dir)
    assert python_file.name not in os.listdir(directory)
    return src_dir.resolve()


def create_python_file(directory: Path):
    content = """
    def add(a,b):
        return a + b
    """

    file_path = Path(directory) / "main.py"
    with open(file_path, "w") as f:
        f.write(content)

    assert file_path.name == "main.py"
    assert file_path.name in os.listdir(directory)
    return file_path.resolve()

# ----------------------------------------------------

def create_image(tmpdir:Path):
    python_file_path = create_python_file(tmpdir)
    test_file_path = create_test_file(tmpdir, python_file_path)
    dockerfile_path = create_dockerfile(tmpdir, test_file_path)
    img = build_image(tmpdir, dockerfile_path)
    return img


def build_image(directory:Path, dockerfile_path: Path):
    client = docker.from_env()
    image, logs = client.images.build(
        path=str(directory),
        dockerfile=dockerfile_path.name,
        tag = f"{os.getenv("DOCKERHUB_USERNAME")}/test_repository:latest",
        rm=True
    )
    return image


def upload_image(image):
    client = docker.from_env()
    client.login(
        username=os.getenv("DOCKERHUB_USERNAME"),
        password=os.getenv("DOCKERHUB_PASSWORD"),
        registry="https://index.docker.io/v1/"
    )
    print(image.tags)

    repository = image.tags[0].split(":")[0]
    tag = image.tags[0].split(":")[1]
    client.images.push(
        repository=repository,
        tag=tag
    )
    return repository + ":" + tag



def create_dockerfile(directory: Path, test_file_path: Path):
    content = f"""
    FROM python:3.11-slim
    WORKDIR /app
    RUN pip install pytest
    RUN mkdir src output
    COPY {test_file_path.name} .
    CMD python -m pytest > output/score.txt
    """

    with open(f"{directory}/Dockerfile", "w") as f:
        f.write(content)

    assert "Dockerfile" in os.listdir(directory)
    return (Path(directory) / "Dockerfile").resolve()


def create_test_file(directory: Path, python_file_path: Path):
    content = f"""
    from src.{python_file_path.name} import add
    def test_add():
    assert add(1, 2) == 3
    assert add(1, -1) == 0
    assert add(-1, -1) == -2
    assert add(0, 0) == 0
    """

    file_path = Path(directory) / f"test_{python_file_path.name}"
    with open(file_path, "w") as f:
        f.write(content)

    assert file_path.name in os.listdir(directory)
    return file_path.resolve()
