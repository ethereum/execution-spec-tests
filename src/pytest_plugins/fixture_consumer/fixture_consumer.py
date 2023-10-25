"""
A pytest plugin to execute the blocktest on the specified fixture directory.
"""

from pathlib import Path


def pytest_addoption(parser):  # noqa: D103
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--fixture-directory",
        type=Path,
        action="store",
        default="fixtures",
        help="Specify the fixture directory to execute tests on.",
    )
