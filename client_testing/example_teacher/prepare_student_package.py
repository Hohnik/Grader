#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import yaml


def create_student_package(
    course_name: str,
    server_url: str,
    template_dir: str,
    output_dir: str = "student_package",
):
    """
    Create a package for students containing:
    - submit.py
    - config.yaml (pre-filled with course details)
    - src/ (with template files)
    - README.md
    - requirements.txt
    """
    # Create output directory
    output_path = Path(output_dir)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir()

    # Copy template files
    print(f"Copying template files from {template_dir}...")
    template_path = Path(template_dir)
    if not template_path.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Create src directory and copy template files
    src_path = output_path / "src"
    src_path.mkdir()
    for file in template_path.glob("*"):
        if file.is_file():
            shutil.copy2(file, src_path)

    # Copy submit script and README
    script_dir = Path(__file__).parent
    shutil.copy2(script_dir / "submit.py", output_path)
    shutil.copy2(script_dir / "README.md", output_path)
    shutil.copy2(script_dir / "requirements.txt", output_path)

    # Create config.yaml with course details
    config = {
        "student_name": "YOUR_NAME_HERE",
        "course_name": course_name,
        "server_url": server_url,
    }

    with open(output_path / "config.yaml", "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)

    print(f"\nStudent package created in: {output_path}")
    print("It contains:")
    for item in output_path.iterdir():
        print(f"- {item.name}")


def main():
    print("📦 Student Package Preparation Tool")
    print("==================================")

    # Get course details from professor
    course_name = input("Enter course name (e.g., python-intro-2024): ").strip()
    server_url = input(
        "Enter grading server URL (default: http://localhost:8000): "
    ).strip()
    if not server_url:
        server_url = "http://localhost:8000"

    template_dir = input("Enter path to template files: ").strip()
    output_dir = input(
        "Enter output directory name (default: student_package): "
    ).strip()
    if not output_dir:
        output_dir = "student_package"

    try:
        create_student_package(course_name, server_url, template_dir, output_dir)
        print("\n✅ Package created successfully!")
        print(f"You can now distribute the '{output_dir}' directory to your students.")
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")


if __name__ == "__main__":
    main()
