"""
CLI interface for common EEST shortcuts and utilities.
"""

import argparse
import os
import subprocess

from logger import setup_logger

logger = setup_logger(__name__)


def initialize_repository():
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


def clean_repository():
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


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="EEST utilities")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Performs all initialization steps for the repository",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Removes .tox, .pytest_cache, .mypy_cache, venv & fixtures from the repository",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Performs a clean and init on the repository",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Outputs the version of the repository",
    )
    args = parser.parse_args()

    if args.clean or args.reset:
        clean_repository()
        logger.info("Repository cleaned!")

    if args.init or args.reset:
        initialize_repository()
        logger.info("Repository initialized!")

    if args.version:
        logger.info("Version: 0.1.0 - TODO")


if __name__ == "__main__":
    main()
