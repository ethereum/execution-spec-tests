"""
CLI interface for common EEST shortcuts and utilities.
"""

import logging
import os
import shutil
import subprocess

import click
import colorlog


def setup_logger():
    """
    Custom logger setup for EEST CLI.
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s%(reset)s[%(asctime)s] %(message)s",
            datefmt="%m-%d|%H:%M:%S",
            log_colors={"INFO": "green", "WARNING": "yellow"},
        )
    )
    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logger()


@click.group()
def eest():
    """
    EEST commands group for common shortcuts and utilities.
    """
    pass


@eest.command()
def init():
    """
    Initializes and installs all required packages add dependencies for the repository:
    ```
    python3 -m venv ./venv/
    pip install -e '.[docs,lint,test]'
    solc-select use latest --always-install
    ```
    """
    logger.info("Creating a virtual environment: `python3 -m venv ./venv/`")
    subprocess.run(["python3", "-m", "venv", "./venv/"], check=True)
    pip_path = os.path.join(".", "venv", "bin", "pip")

    logger.info("Upgrading pip to the latest version: `pip install --upgrade pip`")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)

    logger.info("Installing required packages: `pip install -e '.[docs,lint,test]'`")
    subprocess.run([pip_path, "install", "-e", ".[docs,lint,test]"], check=True)

    logger.info("Installing latest solc within venv: `solc-select use latest --always-install`")
    original_home = os.environ.get("HOME")
    # solc-select uses $HOME to store the solc binaries, so temporarily change it to the venv
    os.environ["HOME"] = "./venv"
    solc_select_path = os.path.join(".", "venv", "bin", "solc-select")
    subprocess.run([solc_select_path, "use", "latest", "--always-install"], check=True)
    # revert the $HOME environment variable
    os.environ["HOME"] = original_home


@eest.command()
def clean():
    """
    Cleans the repository of all generated files and directories:
    ```
    rm -rf .tox .cache .pytest_cache .mypy_cache venv fixtures build
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
    Entry point such that the CLI can be run with `python -m eest_utils`.
    """
    eest()


if __name__ == "__main__":
    eest()
