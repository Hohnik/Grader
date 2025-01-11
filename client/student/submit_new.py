import os
import shutil
import sys
from pathlib import Path

import httpx
import yaml


def load_config(config_path: str = "config.yaml"):
    """Load configuration from yaml file"""
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found: {config_path}")
        print("Make sure config.yaml exists in the same directory as this script")
        sys.exit(1)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Validate required fields
        required_fields = ["student_name", "course_name", "server_url"]
        for field in required_fields:
            if not config.get(field):
                print(f"Error: Missing or empty required field: {field}")
                sys.exit(1)

        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)


def submit_assignment(config, src_dir: Path = Path("src")):
    """Submit the assignment to the grading server"""
    # Validate source directory
    if not src_dir.exists():
        print(f"Error: Source directory not found: {src_dir}")
        print("Make sure your code is in the 'src' directory")
        sys.exit(1)

    # Check if directory is empty (ignoring __pycache__)
    has_files = False
    for item in src_dir.iterdir():
        if item.name != "__pycache__" and not item.name.startswith("."):
            has_files = True
            break

    if not has_files:
        print(f"Error: Source directory is empty: {src_dir}")
        print("Make sure you have added your code files")
        sys.exit(1)

    # Create submission zip
    zip_path = Path("submission.zip")
    try:
        print("Zipping your code...")
        shutil.make_archive("submission", "zip", src_dir)

        # Prepare submission
        files = {"submission": open(zip_path, "rb")}
        data = {
            "student_name": config["student_name"],
            "course_name": config["course_name"],
        }

        # Submit assignment
        print("Submitting to grading server...")
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{config['server_url']}/student/submit", files=files, data=data
                )
                response.raise_for_status()
                result = response.json()

                print("\nSubmission successful! 🎉")
                print(f"Score: {result.get('score', 'N/A')}")
                print(f"Feedback: {result.get('feedback', 'No feedback available')}")
                return result

        except httpx.ConnectError as e:
            print(f"\nError submitting assignment: {e}")
            raise
        except httpx.HTTPError as e:
            print(f"\nError submitting assignment: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Server response: {e.response.text}")
            sys.exit(1)

    finally:
        # Cleanup
        if zip_path.exists():
            zip_path.unlink()


def main():
    print("📚 Assignment Submission Tool")
    print("============================")

    # Load configuration
    config = load_config()

    # Submit the assignment
    submit_assignment(config)


if __name__ == "__main__":
    main()
