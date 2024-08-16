"""
Pytest plugin to create a temporary folder for the session where multi-process tests can store data
that is shared between processes.
"""

import os
import shutil
from pathlib import Path
from tempfile import gettempdir as get_temp_dir  # noqa: SC200
from typing import Generator

import pytest
from filelock import FileLock


@pytest.fixture(scope="session")
def session_temp_folder(testrun_uid: str) -> Generator[Path, None, None]:  # noqa: D103, SC200
    """
    Create a global temporary folder that will be shared among all the
    xdist workers to coordinate the tests.

    "testrun_uid" is a fixture provided by the xdist plugin, and is unique for each test run,
    so it is used to create the unique folder name for each test run.

    We also create a file to keep track of how many workers are still using the folder, so we can
    delete it when the last worker is done.
    """
    session_temp_folder = Path(get_temp_dir()) / f"pytest-{testrun_uid}"
    session_temp_folder.mkdir(exist_ok=True)

    folder_users_file_name = "folder_users"
    folder_users_file = session_temp_folder / folder_users_file_name
    folder_users_lock_file = session_temp_folder / f"{folder_users_file_name}.lock"

    with FileLock(folder_users_lock_file):
        if folder_users_file.exists():
            with folder_users_file.open("r") as f:
                folder_users = int(f.read())
        else:
            folder_users = 0
        folder_users += 1
        with folder_users_file.open("w") as f:
            f.write(str(folder_users))

    yield session_temp_folder

    with FileLock(folder_users_lock_file):
        with folder_users_file.open("r") as f:
            folder_users = int(f.read())
        folder_users -= 1
        if folder_users == 0:
            shutil.rmtree(session_temp_folder)
        else:
            with folder_users_file.open("w") as f:
                f.write(str(folder_users))


@pytest.fixture(scope="session")
def worker_count() -> int:
    """
    Get the number of workers for the test.
    """
    worker_count_env = os.environ.get("PYTEST_XDIST_WORKER_COUNT")
    if not worker_count_env:
        return 1
    return max(int(worker_count_env), 1)
