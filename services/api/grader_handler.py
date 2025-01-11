from grader.grader import spawn_container


async def grade_submission(submission_id: int, submission_directory: str) -> str:
    score_url = await spawn_container(submission_id, submission_directory)
    return score_url
