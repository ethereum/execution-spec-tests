"""
Common pytest fixtures for ethereum_test_tools tests.
"""

import pytest
from semver import Version

from ..code import SOLC_SUPPORTED_VERSIONS, Yul

SOLC_PADDING_VERSION = Version.parse("0.8.21")


@pytest.fixture(scope="session")
def solc_version() -> Version:
    """Return the version of solc being used for tests."""
    solc_version = Yul("").version().finalize_version()
    if solc_version not in SOLC_SUPPORTED_VERSIONS:
        raise Exception("Unsupported solc version: {}".format(solc_version))
    return solc_version
