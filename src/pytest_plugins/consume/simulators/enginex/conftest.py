"""
Pytest fixtures for the `consume enginex` simulator.

Configures the hive back-end & EL clients for test execution with BlockchainEngineXFixtures.
"""

import logging

import pytest
from hive.client import Client

from ethereum_test_exceptions import ExceptionMapper
from ethereum_test_fixtures import BlockchainEngineXFixture
from ethereum_test_rpc import EngineRPC

logger = logging.getLogger(__name__)

pytest_plugins = (
    "pytest_plugins.pytest_hive.pytest_hive",
    "pytest_plugins.consume.simulators.base",
    "pytest_plugins.consume.simulators.multi_test_client",
    "pytest_plugins.consume.simulators.test_case_description",
    "pytest_plugins.consume.simulators.timing_data",
    "pytest_plugins.consume.simulators.exceptions",
    "pytest_plugins.consume.simulators.helpers.test_tracker",
)


def pytest_configure(config):
    """Set the supported fixture formats for the engine simulator."""
    config._supported_fixture_formats = [BlockchainEngineXFixture.format_name]


@pytest.fixture(scope="module")
def test_suite_name() -> str:
    """The name of the hive test suite used in this simulator."""
    return "eest/consume-enginex"


@pytest.fixture(scope="module")
def test_suite_description() -> str:
    """The description of the hive test suite used in this simulator."""
    return (
        "Execute blockchain tests against clients using the Engine API with "
        "pre-allocation group optimization using Engine X fixtures."
    )


def pytest_collection_modifyitems(session, config, items):
    """
    Build pre-allocation group test counts during collection phase.

    This hook analyzes all collected test items to determine how many tests
    belong to each pre-allocation group, enabling automatic client cleanup
    when all tests in a group are complete.
    """
    # Only process items for enginex simulator
    if not hasattr(config, "_supported_fixture_formats"):
        return

    if BlockchainEngineXFixture.format_name not in config._supported_fixture_formats:
        return

    # Get the test tracker from session if available
    test_tracker = getattr(session, "_pre_alloc_group_test_tracker", None)
    if test_tracker is None:
        # Tracker will be created later by the fixture, store counts on session for now
        group_counts = {}
        for item in items:
            if hasattr(item, "callspec") and "test_case" in item.callspec.params:
                test_case = item.callspec.params["test_case"]
                if hasattr(test_case, "pre_hash"):
                    pre_hash = test_case.pre_hash
                    group_counts[pre_hash] = group_counts.get(pre_hash, 0) + 1

        # Store on session for later retrieval by test_tracker fixture
        session._pre_alloc_group_counts = group_counts
        logger.info(
            f"Collected {len(group_counts)} pre-allocation groups with tests: {dict(group_counts)}"
        )
    else:
        # Update tracker directly if it exists
        group_counts = {}
        for item in items:
            if hasattr(item, "callspec") and "test_case" in item.callspec.params:
                test_case = item.callspec.params["test_case"]
                if hasattr(test_case, "pre_hash"):
                    pre_hash = test_case.pre_hash
                    group_counts[pre_hash] = group_counts.get(pre_hash, 0) + 1

        for pre_hash, count in group_counts.items():
            test_tracker.set_group_test_count(pre_hash, count)

        logger.info(f"Updated test tracker with {len(group_counts)} pre-allocation groups")


@pytest.fixture(scope="function")
def engine_rpc(client: Client, client_exception_mapper: ExceptionMapper | None) -> EngineRPC:
    """Initialize engine RPC client for the execution client under test."""
    if client_exception_mapper:
        return EngineRPC(
            f"http://{client.ip}:8551",
            response_validation_context={
                "exception_mapper": client_exception_mapper,
            },
        )
    return EngineRPC(f"http://{client.ip}:8551")
