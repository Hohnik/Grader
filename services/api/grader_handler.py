from grader.grader import spawn_container


async def grade_submission(submission_directory: str) -> str:
    score_url = await spawn_container(submission_directory)
    return score_url
