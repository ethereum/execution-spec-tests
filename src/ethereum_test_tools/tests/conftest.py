"""
Common pytest fixtures for ethereum_test_tools tests.
"""

import pytest

from ..code import Code, Initcode, Yul

SUPPORTED_SOLC_VERSIONS = ["0.8.20", "0.8.21"]


@pytest.fixture(scope="session")
def solc_version():
    """Return the version of solc being used for tests."""
    solc_version = Yul("").version().split("+")[0]
    if solc_version not in SUPPORTED_SOLC_VERSIONS:
        raise Exception("Unsupported solc version: {}".format(solc_version))
    return solc_version
