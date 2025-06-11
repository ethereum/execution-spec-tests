"""Pytest fixtures for the engine (restart) simulator."""

import pytest

from ethereum_test_fixtures import BlockchainEngineFixture


def pytest_configure(config):
    """Set the supported fixture formats for the engine simulator."""
    config._supported_fixture_formats = [BlockchainEngineFixture.format_name]


@pytest.fixture(scope="module")
def test_suite_name() -> str:
    """The name of the hive test suite used in this simulator."""
    return "eest/consume-engine"


@pytest.fixture(scope="module")
def test_suite_description() -> str:
    """The description of the hive test suite used in this simulator."""
    return "Execute blockchain tests against clients using the Engine API."
