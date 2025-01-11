import asyncio
import logging
import time

import docker
import docker.errors
from docker.models.containers import Container

termination_tasks = {}


async def spawn_container(directory: str) -> str:
    """
    Spawns a container from the given directory and returns the score.
    """
    logging.info(f"Starting container spawn")
    try:
        client = docker.DockerClient(
            base_url="unix://var/run/docker.sock", version="auto"
        )

        try:
            logging.debug(f"Building Docker image")
            image = client.images.build(
                path=directory, rm=True, forcerm=True, pull=False
            )[0]
        except docker.errors.BuildError as e:
            logging.error(f"Failed to build Docker image - Error: {str(e)}")
            raise
        logging.debug(f"Docker image built successfully")

        assert image.id
        container = client.containers.run(
            image=image.id,
            name=f"submission_{directory.split('/')[-1]}",
            detach=True,
            mem_limit="512m",  # Limit memory to prevent DOS
            cpu_period=100000,
            cpu_quota=50000,  # Limit CPU to 50% of one core
        )
        assert container.id
        logging.info(f"Container started successfully - ID: {container.id[:12]}")

        termination_tasks[container.id] = asyncio.create_task(
            terminate_container(container, time.time() + 5 * 60)
        )

        return await score(container)

    except Exception as e:
        logging.error(f"Container execution failed - Error: {str(e)}")
        raise


async def terminate_container(container, timeout):
    await asyncio.sleep(timeout)
    try:
        container.kill()
        container.remove()

    finally:
        del termination_tasks[container.id]


async def score(container: Container):
    while container.status == "running":
        await asyncio.sleep(5)
        container.reload()
    logging.info(
        f"Container {container.id[:12] if container.id else container.id} finished."
    )

    bits, _ = container.get_archive("/app/score.txt")
    file_content = b"".join(bits)

    container.remove(force=True)

    return str(file_content)
