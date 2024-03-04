"""
CLI interface for common EEST shortcuts and utilities.
"""

import logging
import os
import shutil
import subprocess
import sys

import click
import colorlog

# Required for forks < Constantinople
SOLC_PRE_CONSTANTINOPLE = "0.8.21"


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
    python -m venv ./venv/
    pip install --upgrade pip
    pip install -e '.[docs,lint,test]' --force-reinstall
    solc-select install 0.8.21
    solc-select use latest --always-install
    ```
    """
    if not (3, 10, 0) <= sys.version_info[:3] <= (3, 12, 2):
        raise RuntimeError("EEST requires Python 3.10.0 up to 3.12.2.")
    python_path = shutil.which("python")
    venv_create = [python_path, "-m", "venv", os.path.join(".", "venv")]

    logger.info(f"Creating a virtual environment: `{' '.join(venv_create)}`")
    subprocess.run(venv_create, check=True)

    pip_path = os.path.join(".", "venv", "bin", "pip")

    pip_upgrade = [pip_path, "install", "--upgrade", "pip"]
    logger.info(f"Upgrading pip to the latest version: `{' '.join(pip_upgrade)}`")
    subprocess.run(pip_upgrade, check=True)

    pip_install = [pip_path, "install", "-e", ".[docs,lint,test]", "--force-reinstall"]
    logger.info(f"Installing required packages: `{' '.join(pip_install)}`")
    subprocess.run(pip_install, check=True)

    solc_select_path = os.path.join(".", "venv", "bin", "solc-select")
    os.environ["VIRTUAL_ENV"] = os.environ.get("VIRTUAL_ENV")

    # Required for forks < Constantinople, see important note within release note:
    # https://github.com/ethereum/solidity/releases/tag/v0.8.22
    solc_install_0_8_21 = [solc_select_path, "install", SOLC_PRE_CONSTANTINOPLE]
    logger.info(f"Installing solc 0.8.21 within venv:  `{' '.join(solc_install_0_8_21)}`")
    subprocess.run(solc_install_0_8_21, check=True)

    solc_install_latest = [solc_select_path, "use", "latest", "--always-install"]
    logger.info(
        f"Installing and using latest solc within venv:  `{' '.join(solc_install_latest)}`"
    )
    subprocess.run(solc_install_latest, check=True)


@eest.command()
def clean(remove_venv: bool = False):
    """
    Cleans the repository of all generated files and directories:
    ```
    rm -rf .tox .cache .pytest_cache .mypy_cache fixtures build venv
    ```
    By default, the virtual environment is not removed.
    """
    items_to_remove = [".tox", ".pytest_cache", ".mypy_cache", "fixtures", "build", "site", "venv"]
    for item in items_to_remove:
        if os.path.exists(item):
            if item == "venv" and not remove_venv:
                continue
            shutil.rmtree(item, ignore_errors=True)
            logger.warning(f"Deleted `{item}`")


@eest.command()
def reset():
    """
    Performs a clean and init on the repository (deletes the virtual env).
    """
    ctx = click.get_current_context()
    ctx.invoke(clean, remove_venv=True)
    ctx.invoke(init)


# TODO: add this command to the CLI within the versioning PR
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
