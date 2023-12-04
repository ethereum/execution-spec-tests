"""
A hive simulator that executes test fixtures in the blockchain test format
against clients by providing them a genesis state and blocks via the Engine
API.

Implemented using the pytest framework as a pytest plugin.
"""
import pytest


@pytest.fixture(scope="session")
def test_suite_name() -> str:
    """
    The name of the hive test suite used in this simulator.
    """
    return "EEST Consume Blocks via Engine API"


@pytest.fixture(scope="session")
def test_suite_description() -> str:
    """
    The description of the hive test suite used in this simulator.
    """
    return "Execute blockchain tests by sending blocks to a client via the Engine API."
