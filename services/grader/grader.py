import asyncio
import logging
import os
from pathlib import Path


async def spawn_container(sub_dir: str, container_url: str) -> str:
    """
    Runs the prebuilt Docker container (from Docker Hub) using the provided submission
    and returns the absolute filepath of the output score.txt file.

    This function assumes that:
     - student code will be mounted to sub_dir/src/
     - the Docker container writes the score output to sub_dir/output/score.txt.
    """
    logging.info(f"Spawning Docker container with image: {container_url}")

    base_path = Path(sub_dir).resolve()
    src_path = base_path / "src"
    output_path = base_path / "output"
    score_file_path = output_path / "score.txt"
    
    assert src_path.exists(), "src/ missing"
    assert src_path.is_dir(), "src/ must be directory"
    assert output_path.exists(), "output/ missing"
    assert output_path.is_dir(), "output/ must be directory"

    logging.info(f"Base directory contents: {os.listdir(base_path)}")
    logging.info(f"Source directory contents: {os.listdir(src_path)}")

    # Check if Docker is available
    try:
        check_cmd = "docker --version"
        check_process = await asyncio.create_subprocess_shell(
            check_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        check_stdout, check_stderr = await check_process.communicate()
        
        if check_process.returncode != 0:
            raise RuntimeError(f"Docker not available: {check_stderr.decode().strip()}")
        
        logging.info(f"Docker version: {check_stdout.decode().strip()}")
    except Exception as e:
        raise RuntimeError(f"Failed to check Docker: {str(e)}")

    # Pull the image first to ensure it exists and to get a clearer error if it doesn't
    try:
        pull_cmd = f"docker pull {container_url}"
        logging.info(f"Pulling Docker image: {pull_cmd}")
        
        pull_process = await asyncio.create_subprocess_shell(
            pull_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        pull_stdout, pull_stderr = await pull_process.communicate()
        
        if pull_process.returncode != 0:
            error_msg = pull_stderr.decode().strip()
            logging.error(f"Failed to pull Docker image: {error_msg}")
            raise RuntimeError(f"Failed to pull Docker image: {error_msg}")
        
        logging.info("Docker image pulled successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to pull Docker image: {str(e)}")

    # Construct Docker run command with absolute paths
    cmd = (
        "docker run --rm "
        f'-v "{src_path}:/app/src/" '
        f'-v "{output_path}:/app/output/" '
        f"{container_url}"
    )
    
    logging.info(f"Running container with command: {cmd}")

    try:
        command = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await command.communicate()
        
        stdout_text = stdout.decode().strip()
        stderr_text = stderr.decode().strip()
        
        if stdout_text:
            logging.info(f"Container stdout: {stdout_text}")
        
        if stderr_text:
            logging.warning(f"Container stderr: {stderr_text}")

        # Log the return code but don't treat it as an error
        logging.info(f"Container exited with code {command.returncode}")
        
        # Only consider it a container execution error if the score file isn't created
        score_file_path = output_path / "score.txt"
        if not score_file_path.exists():
            error_msg = stderr_text or stdout_text or "No error output but score file wasn't created"
            logging.error(f"Container execution failed: {error_msg}")
            raise RuntimeError(f"Container execution failed: {error_msg}")
            
        logging.info("Container executed and score file was created successfully.")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logging.exception("Exception while running container")
        raise RuntimeError(f"Failed to run container: {str(e)}")
        
    # Check that the score file exists and has content
    if not score_file_path.exists():
        logging.error("Container did not generate a score.txt file")
        raise FileNotFoundError(f"Expected score file not found at {score_file_path}")
    
    # Optionally check for empty score file
    if score_file_path.stat().st_size == 0:
        logging.warning("Score file was created but is empty")
    
    logging.info(f"Score file created at {score_file_path}")
    return str(score_file_path)


if __name__ == "__main__":
    # set logging level to DEBUG to see all messages
    logging.basicConfig(level=logging.DEBUG)
    sub_dir = "./example_submission"
    container_url = "hohniki/teacher_test:latest"

    score_file = asyncio.run(spawn_container(sub_dir, container_url))
    print(f"Score file available at: {score_file}")
