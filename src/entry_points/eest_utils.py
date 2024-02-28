"""
CLI interface for common EEST shortcuts and utilities.
"""

import os
import shutil
import subprocess

import click

from logger import setup_logger

logger = setup_logger(__name__)


@click.group()
def eest():
    """
    EEST commands for common repo utilities.
    """
    pass


@eest.command()
def init():
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


@eest.command()
def clean():
    """
    Cleans the repository of all generated files and directories:
    ```
    rm -rf .tox .pytest_cache .mypy_cache venv fixtures
    ```
    """
    items_to_remove = [".tox", ".pytest_cache", ".mypy_cache", "venv", "fixtures"]
    for item in items_to_remove:
        if os.path.exists(item):
            shutil.rmtree(item, ignore_errors=True)
            logger.warning(f"Deleted `{item}`")


@eest.command()
def reset():
    """
    Performs a clean and init on the repository.
    """
    ctx = click.get_current_context()
    ctx.invoke(clean)
    ctx.invoke(init)


# TODO:
@eest.command()
def version():
    """
    Outputs the version of the repository.
    """
    logger.info("Version: 0.1.0 - TODO")


def main():
    """
    Entry point for EEST commands.
    """
    eest()


if __name__ == "__main__":
    eest()
