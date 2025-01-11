import asyncio
import io
import logging
import os
import re
import shutil
import tarfile
import time

import docker
import docker.errors
from docker.models.containers import Container

# Container-related tasks dictionary
termination_tasks = {}


def course_ok(course):
    with open("db/courses.txt", "r") as f:
        return course in [line.strip() for line in f]


def student_ok(name):
    with open("db/students.txt", "r") as f:
        return name in [line.strip() for line in f]


def cleanup_student_directory(directory: str):
    """
    Cleans up the student directory, keeping only the source code and score file
    """
    try:
        # Remove Dockerfile, requirements.txt, and tests directory
        if os.path.exists(f"{directory}/Dockerfile"):
            os.remove(f"{directory}/Dockerfile")
        if os.path.exists(f"{directory}/requirements.txt"):
            os.remove(f"{directory}/requirements.txt")
        if os.path.exists(f"{directory}/tests"):
            shutil.rmtree(f"{directory}/tests")

        # Remove any zip files in the directory
        for file in os.listdir(directory):
            if file.endswith(".zip"):
                os.remove(os.path.join(directory, file))
                logging.debug(f"Removed zip file: {file}")

        logging.debug(f"Cleaned up directory: {directory}")
    except Exception as e:
        logging.error(f"Error during cleanup - Directory: {directory}, Error: {str(e)}")


async def spawn_container(id: int, directory: str) -> str:
    """
    Spawns a container from the given directory and returns the path to the score.txt file
    """
    logging.info(f"Starting container spawn - Task: {id}")
    try:
        # Initialize Docker client with low-level API
        client = docker.APIClient(
            base_url="unix://var/run/docker.sock",
            version="auto",
            timeout=5 * 60,
            credstore_env={},  # Empty dict to prevent credential store usage
        )

        # Convert to high-level client for container management
        high_level_client = docker.DockerClient(
            base_url="unix://var/run/docker.sock",
            version="auto",
        )

        # Check if Docker daemon is running
        client.ping()
    except docker.errors.DockerException as e:
        logging.error(f"Docker daemon connection failed - Error: {str(e)}")
        raise RuntimeError("Docker service is not available") from e

    try:
        # Build image using low-level API
        logging.debug(f"Building Docker image - Task: {id}")
        image_id = None
        for line in client.build(
            path=directory, rm=True, forcerm=True, pull=False, decode=True
        ):
            if "stream" in line:
                logging.debug(line["stream"].strip())
            if "aux" in line and "ID" in line["aux"]:
                image_id = line["aux"]["ID"]

        if not image_id:
            raise RuntimeError("Failed to build Docker image")

        logging.debug(f"Docker image built successfully - Task: {id}")

        # Use high-level API for container management
        container = high_level_client.containers.run(
            image=image_id,
            name=f"student_{id}",
            detach=True,
            mem_limit="512m",  # Limit memory to prevent DOS
            cpu_period=100000,
            cpu_quota=50000,  # Limit CPU to 50% of one core
        )

        # Check if container started successfully
        container.reload()
        if container.status != "running":
            raise RuntimeError(f"Container failed to start. Status: {container.status}")

        logging.info(f"Container started successfully - ID: {container.id}, Task: {id}")

        # Set 5 minute timeout for container execution
        termination_tasks[container.id] = asyncio.create_task(
            terminate_container(container, time.time() + 5 * 60)
        )

        score_tar = await await_score(container)
        score_tar = io.BytesIO(score_tar)

        with tarfile.open(fileobj=score_tar, mode="r") as tar:
            member = tar.getmembers()[0]
            score = tar.extractfile(member)
            score_url = f"{directory}/score.txt"
            if score:
                score = score.read()
                with open(score_url, "w", encoding="utf-8") as txt_file:
                    txt_file.write(score.decode("utf-8"))
            logging.info(f"Score file saved - Task: {id}, Path: {score_url}")

        return f"{directory}/score.txt"

    except Exception as e:
        logging.error(f"Container execution failed - Task: {id}, Error: {str(e)}")
        # Clean up container if it exists
        try:
            container.remove(force=True)
        except docker.errors.NotFound:
            pass
        raise


async def terminate_container(container, timeout):
    await asyncio.sleep(timeout)
    try:
        container.kill()
        container.remove()
        logging.info(f"Container terminated - ID: {container.id[:12]}")

    finally:
        del termination_tasks[container.id]


def parse_pytest_output(output: str) -> tuple[float, float]:
    """
    Parse pytest output to extract weighted scores from tests
    Returns tuple of (weighted_passed, total_weight)
    """
    # First look for test results with weights in the output
    # Example: test_basic[weight=2] PASSED
    test_pattern = r"test_\w+(?:\[weight=(\d+)\])?\s+(PASSED|FAILED|ERROR)"
    tests = re.finditer(test_pattern, output, re.MULTILINE)

    weighted_passed = 0.0
    total_weight = 0.0

    for test in tests:
        # Get weight (default to 1 if not specified)
        weight = float(test.group(1)) if test.group(1) else 1.0
        result = test.group(2)

        total_weight += weight
        if result == "PASSED":
            weighted_passed += weight

    # If no tests found with explicit weights, fall back to simple counting
    if total_weight == 0:
        # Look for the test summary line, e.g. "4 passed, 2 failed in 0.05s"
        summary_pattern = r"=+ (.+) in \d+\.\d+s =+"
        match = re.search(summary_pattern, output)

        if not match:
            logging.error("Could not find test summary in pytest output")
            return (0.0, 0.0)

        summary = match.group(1)

        # Count passed tests
        passed = 0
        if "passed" in summary:
            passed_match = re.search(r"(\d+) passed", summary)
            if passed_match:
                passed = int(passed_match.group(1))

        # Count total tests (passed + failed + errors)
        total = passed
        if "failed" in summary:
            failed_match = re.search(r"(\d+) failed", summary)
            if failed_match:
                total += int(failed_match.group(1))
        if "error" in summary:
            error_match = re.search(r"(\d+) error", summary)
            if error_match:
                total += int(error_match.group(1))

        return (float(passed), float(total))

    return (weighted_passed, total_weight)


def calculate_score(weighted_passed: float, total_weight: float) -> int:
    """
    Calculate percentage score based on weighted passed tests and total weight
    Returns score from 0-100
    """
    if total_weight == 0:
        logging.warning("No tests found, returning score of 0")
        return 0
    return round((weighted_passed / total_weight) * 100)


async def await_score(container: Container):
    """
    returns the score.txt file from the container in tar format
    """
    while container.status == "running":
        await asyncio.sleep(5)
        container.reload()
    logging.info(f"Container stopped running - ID: {container.id}")

    # Get pytest output from container logs
    logs = container.logs().decode("utf-8")
    passed_tests, total_tests = parse_pytest_output(logs)
    score = calculate_score(passed_tests, total_tests)

    # Create score file with detailed information
    score_content = f"""{score}/100
Passed Tests: {passed_tests}
Total Tests: {total_tests}

Detailed Test Output:
{logs}"""

    # Create a temporary file with the score
    with open("temp_score.txt", "w") as f:
        f.write(score_content)

    # Create tar archive of the score file
    with tarfile.open("score.tar", "w") as tar:
        tar.add("temp_score.txt", arcname="score.txt")

    with open("score.tar", "rb") as f:
        score_tar = f.read()

    # Clean up temporary files
    os.remove("temp_score.txt")
    os.remove("score.tar")

    logging.debug(
        f"Score calculated - Passed: {passed_tests}/{total_tests}, Score: {score}/100"
    )
    container.remove(force=True)

    return score_tar
