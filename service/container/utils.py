import asyncio
import logging
import time

import docker
from docker.models.containers import Container

termination_tasks = {}


async def spawn_container(id: int, directory: str) -> str:
    """
    Spawns a container from the given directory and returns the path to the score.txt file
    """
    logging.info(f"Spawning container for student {id} from directory {directory}")
    client = docker.from_env(timeout=5 * 60)

    image, build_logs = client.images.build(path=directory, rm=True)
    container = client.containers.run(image=image, name=f"student_{id}", detach=True)

    termination_tasks[container.id] = asyncio.create_task(
        terminate_container(container, time.time() + 1 * 60)
    )

    file_content = await await_score(container)
    with open(f"{directory}/score.txt", "wb") as f:
        f.write(file_content)

    for line in build_logs:
        print(line)

    return f"{directory}/score.txt"


async def terminate_container(container, timeout):
    await asyncio.sleep(timeout)
    try:
        container.kill()
        container.remove()

    finally:
        del termination_tasks[container.id]


async def await_score(container: Container):
    while container.status == "running":
        await asyncio.sleep(5)
        container.reload()
    print(f"Container '{container.id}' is no longer running. Terminating...")

    bits, stat = container.get_archive("/app/score.txt")
    file_content = b"".join(bits)

    print("Stats:", stat)

    container.remove(force=True)

    return file_content
