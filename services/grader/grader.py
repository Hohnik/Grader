import asyncio
import time
from collections.abc import Container

import docker

client = docker.from_env()


termination_tasks = {}

course_container_mapping = {"Programmieren III": "programmieren3"}


async def spawn_container(id: int, student_name: str, course_name: str) -> str:

    sub_file_url: str = f"submissions/{course_name}/{student_name}/{id}.zip"
    image_name = dockerfile = course_container_mapping[course_name]
    container_name = f"{image_name}_{student_name}_{id}"

    with open(f"container/dockerfiles/{dockerfile}", "rb") as dockerfile:
        _, build_logs = client.images.build(
            fileobj=dockerfile, tag=f"{image_name}", rm=True
        )

    # NOTE: Remove in prod, just for debugging
    for line in build_logs:
        print(line)

    container = client.containers.run(
        image=image_name, name=container_name, detach=True
    )

    timeout = time.time() + 5 * 60  # NOTE: fetch this from lecturer configs
    termination_tasks[container.id] = asyncio.create_task(
        terminate_container(container, timeout)
    )

    return "8/10"


async def terminate_container(container, timeout):
    await asyncio.sleep(timeout)
    try:
        container.kill()
        container.remove()

    finally:
        del termination_tasks[container.id]
