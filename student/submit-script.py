import os
import shutil

import requests
import yaml


def main():
    auth = read_config()
    shutil.make_archive("submission", "zip", "src")
    submit_project(auth)
    os.remove("submission.zip")


def submit_project(auth):
    url = "http://0.0.0.0:8000/submit"  # TODO: Relace with real url

    files = {"submission": open("submission.zip", "rb")}
    data = {
        "course_name": auth["course_name"],
        "student_name": auth["student_name"],
    }

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("Submission successful!")
    else:
        print(
            f"Submission failed with {response.status_code}: \
            \nMessage: {response.text}"
        )


def read_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
