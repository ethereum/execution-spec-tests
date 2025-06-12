"""Pytest fixtures for the engine (restart) simulator."""

import pytest

from ethereum_test_base_types import to_json
from ethereum_test_fixtures import BlockchainEngineFixture


@pytest.fixture(scope="module")
def test_suite_name() -> str:
    """The name of the hive test suite used in this simulator."""
    return "eest/consume-engine"


@pytest.fixture(scope="module")
def test_suite_description() -> str:
    """The description of the hive test suite used in this simulator."""
    return "Execute blockchain tests against clients using the Engine API."


@pytest.fixture(scope="function")
def genesis_header(fixture: BlockchainEngineFixture):
    """Get the genesis header from the fixture."""
    return fixture.genesis


