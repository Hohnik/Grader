import asyncio
import logging
import time

import docker
from docker.models.containers import Container

termination_tasks = {}


async def spawn_container(directory: str):
    client = docker.from_env(timeout=5 * 60)

    image, _ = client.images.build(path=directory, rm=True)
    container = client.containers.run(image=image, detach=True)

    termination_tasks[container.id] = asyncio.create_task(
        terminate_container(container, time.time() + 1 * 60)
    )

    return await score(container)


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
