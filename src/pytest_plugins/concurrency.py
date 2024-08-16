"""
Pytest plugin to create a temporary folder for the session where multi-process tests can store data
that is shared between processes.
"""

from argparse import SUPPRESS
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    session_temp_folder_group = parser.getgroup(
        "session_temp_folder", "Arguments defining the temporary folder for the session."
    )
    session_temp_folder_group.addoption(
        "--session-temp-folder",
        action="store",
        dest="session_temp_folder",
        type=Path,
        default=TemporaryDirectory(),
        help=SUPPRESS,
    )


@pytest.fixture(scope="session")
def session_temp_folder(request) -> Path:  # noqa: D103
    return request.config.option.session_temp_folder
