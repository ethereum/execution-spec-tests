"""Pytest configuration and fixtures for the engine reorg simulator."""

import pytest

from ethereum_test_fixtures import BlockchainEngineReorgFixture


def pytest_configure(config):
    """Set the supported fixture formats for the engine simulator."""
    config._supported_fixture_formats = [BlockchainEngineReorgFixture.format_name]


@pytest.fixture(scope="module")
def test_suite_name() -> str:
    """The name of the hive test suite used in this simulator."""
    return "eest/consume-engine-reorg"


@pytest.fixture(scope="module")
def test_suite_description() -> str:
    """The description of the hive test suite used in this simulator."""
    description = (
        "Execute blockchain tests against clients using the Engine API and shared clients using "
        "engine reorg fixtures."
    )
    return description
