from grader.grader import spawn_container


async def grade_submission(submission_directory: str, container_url:str) -> str:
    return await spawn_container(submission_directory, container_url)
