import asyncio
import time

import docker

docker_client = docker.from_env()


termination_tasks = {}

course_container_mapping = {"Programmieren III": "programmieren3.dockerfile"}


async def spawn_container(id: int, course: str, file_url: str):

    dockerfile = course_container_mapping[course]

    # TODO: Create a new container with the given id

    # container = docker_client.containers.run(
    #     image=container_req.image,
    #     command="echo Test",
    #     remove=True,
    # )

    timeout = time.time() + 5 * 60
    termination_tasks[id] = asyncio.create_task(terminate_container(id, timeout))

    return {
        "status": "success",
        "container_id": id,
        "termination_scheduled": time.time() + 5 * 60,
    }


async def terminate_container(container_id, timeout_seconds):
    await asyncio.sleep(timeout_seconds)
    try:
        container = docker_client.containers.get(container_id)
        container.kill()
        container.remove()

    finally:
        del termination_tasks[container_id]
    return 10
