"""
CLI interface for common EEST shortcuts and utilities.
"""

import argparse
import os
import subprocess

from logger import setup_logger

logger = setup_logger(__name__)


def initialize_repository(args):
    """
    Initializes and installs all required packages for the repository:
        ```
        python3 -m venv ./venv/
        source ./venv/bin/activate
        pip install -e '.[docs,lint,test]'
        ```
    """
    logger.info("Creating a virtual environment: `python3 -m venv ./venv/`")
    subprocess.run(["python3", "-m", "venv", "./venv/"], check=True)
    pip_path = os.path.join(".", "venv", "bin", "pip")

    logger.info("Upgrading pip to the latest version: `pip install --upgrade pip`")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

    logger.info("Installing required packages: `pip install -e '.[docs,lint,test]'`")
    subprocess.run([pip_path, "install", "-e", ".[docs,lint,test]"], check=True)


def clean_repository(args):
    """
    Cleans the repository of all generated files and directories:
        ```
        rm -rf .tox .pytest_cache .mypy_cache venv fixtures
        ```
    """
    items_to_remove = [".tox", ".pytest_cache", ".mypy_cache", "venv", "fixtures"]
    for item in items_to_remove:
        if os.path.exists(item):
            subprocess.run(["rm", "-rf", item], check=True)
            logger.warning(f"Deleted `{item}`")


def show_version(args):
    """
    Outputs the version of the repository.
    """
    logger.info("Version: 0.1.0 - TODO")


def main():
    """
    Main function to handle CLI commands and arguments.
    """
    parser = argparse.ArgumentParser(description="EEST utilities")
    subparsers = parser.add_subparsers(help="commands")

    init_parser = subparsers.add_parser("init", help="Initializes the repository")
    init_parser.set_defaults(func=initialize_repository)

    clean_parser = subparsers.add_parser("clean", help="Cleans the repository")
    clean_parser.set_defaults(func=clean_repository)

    reset_parser = subparsers.add_parser(
        "reset", help="Performs a clean and init on the repository"
    )
    reset_parser.set_defaults(
        func=lambda args: (clean_repository(args), initialize_repository(args))
    )

    version_parser = subparsers.add_parser("version", help="Outputs the version of the repository")
    version_parser.set_defaults(func=show_version)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
