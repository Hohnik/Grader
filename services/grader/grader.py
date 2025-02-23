import asyncio
import logging
from pathlib import Path


async def spawn_container(sub_dir: str, container_url: str) -> str:
    """
    Runs the prebuilt Docker container (from Docker Hub) using the provided submission
    and returns the absolute filepath of the output score.txt file.
    
    This function assumes that:
     - student code will be mounted to sub_dir/src/
     - the Docker container writes the score output to sub_dir/output/score.txt.
    """
    logging.info("Spawning Docker container with prebuilt image.")

    base_path = Path(sub_dir).resolve()
    src_path = base_path / "src"
    output_path = base_path / "output"

    # Construct Docker run command with absolute paths.
    # Note: Use quotes to properly escape any spaces in the path.
    cmd = (
        'docker run --rm '
        f'-v "{src_path}:/app/src/" '
        f'-v "{output_path}:/app/output/" '
        'hohniki/teacher_test:latest' # f'{container_url}'
    )


    command = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await command.communicate()

    if command.returncode != 0:
        error_msg = stderr.decode().strip() or stdout.decode().strip()
        logging.error(f"Container execution failed: {error_msg}")
        raise RuntimeError(f"Error running docker container: {error_msg}")
    else:
        logging.info("Container executed successfully.")

    # The container should have written to output/score.txt.
    score_file_path = output_path / "score.txt"

    if not score_file_path.exists():
        logging.error(f"Expected output file {score_file_path} not found.")
        raise FileNotFoundError(f"Output file {score_file_path} not found.")

    logging.info(f"Returning score file path: {score_file_path}")
    return str(score_file_path)


if __name__ == "__main__":
    # set logging level to DEBUG to see all messages
    logging.basicConfig(level=logging.DEBUG)
    sub_dir = "./example_submission"
    container_url = "hohniki/teacher_test:latest"

    score_file = asyncio.run(spawn_container(sub_dir, container_url))
    print(f"Score file available at: {score_file}")
