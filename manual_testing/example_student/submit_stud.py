# /// script
# dependencies = [
#   "pyyaml",
#   "requests",
# ]
# ///

import os
import shutil
import sys
from pathlib import Path

import requests
import yaml


def main():
    print("📚 Assignment Submission Tool")
    config = load_config()
    submit_assignment(config)


def submit_assignment(config, src_dir: Path = Path("src")):
    """Submit the assignment to the grading server"""
    if not any(src_dir.iterdir()):
        print(f"Error: Source directory is empty or not found: {src_dir}")
        sys.exit(1)

    zip_path = Path("submission.zip")
    try:
        shutil.make_archive("submission", "zip", src_dir)

        # Submit assignment
        with open(zip_path, "rb") as file:
            response = requests.post(
                f"{config['server_url']}/student/submit",
                files={"submission": file},
                data={
                    "student_name": config["student_name"],
                    "course_name": config["course_name"],
                },
            )

            if response.status_code == 200:
                result = response.json()
                print( f"{result.get('message', 'N/A')}")
            else:
                print(f"Submission failed with {response.status_code}: {response.text}")
                sys.exit(1)
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        if zip_path.exists():
            zip_path.unlink()


def load_config(config_path: str = "config.yaml"):
    """Load configuration from yaml file"""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Validate required fields
        for field in ["student_name", "course_name", "server_url"]:
            if not config.get(field):
                print(f"Error: Missing or empty required field: {field}")
                sys.exit(1)

        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
