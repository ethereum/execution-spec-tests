"""Common pytest fixtures for ethereum_test_tools tests."""

from pathlib import Path

import pytest
from semver import Version

from ethereum_test_forks import Frontier

from ..code import Solc

SOLC_PADDING_VERSION = Version.parse("0.8.21")


def get_eest_root_folder(marker_files=("pyproject.toml", ".git", "tests", "src")) -> Path:
    """Search for a folder where all files/folders listed above exist (root of project)."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if all((parent / marker).exists() for marker in marker_files):
            return parent
    raise RuntimeError("Project root folder of execution-spec-tests was not found")


@pytest.fixture(scope="session")
def solc_version() -> Version:
    """Return the version of solc being used for tests."""
    solc_version = Solc("").version.finalize_version()

    solc_version_in_use = None

    # on ARM systems that manually compiled solc this can be 0.0.0, so try to recover
    if str(solc_version) == "0.0.0":
        # determine solc version used by solc-select
        #       get eest root folder path
        eest_root: Path = get_eest_root_folder()
        #       get path of solc-select global-version file (stores currently in use solc version)
        solc_version_file_path = eest_root / ".venv" / ".solc-select" / "global-version"
        #       read this file if it exists
        if solc_version_file_path.exists():
            solc_version_in_use = Version.parse(solc_version_file_path.read_text())

    if solc_version < Frontier.solc_min_version() and solc_version_in_use is None:
        raise Exception(f"Unsupported solc version: {solc_version}")

    if solc_version_in_use is not None:
        return solc_version_in_use
    return solc_version
