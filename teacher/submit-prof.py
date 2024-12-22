import os
import shutil

import requests
import yaml


def main():
    config = read_config()
    submit_project(config)


def submit_project(config):
    tests = shutil.make_archive("tests", "zip", "tests")

    url = "http://0.0.0.0:8000/upload"  # TODO: Relace with real url

    files = {
        "tests": open(tests, "rb"), 
        "dockerfile": open("Dockerfile", "rb")
    }
    data = {
        "username": config["username"],
        "password": config["password"],

        "course_name": config["course_name"],
        "start_date": config["start_date"],
        "end_date": config["end_date"],
    }

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("Submission successful!")
    else:
        print(
            f"Submission failed with {response.status_code}: \
            \nMessage: {response.text}"
        )

    os.remove(tests)


def read_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    main()
