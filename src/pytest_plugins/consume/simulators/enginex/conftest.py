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


def pytest_addoption(parser):
    """Add enginex-specific command line options."""
    enginex_group = parser.getgroup("enginex", "EngineX simulator options")
    enginex_group.addoption(
        "--enginex-fcu-frequency",
        dest="enginex_fcu_frequency",
        action="store",
        type=int,
        default=0,
        help=(
            "Control forkchoice update frequency for enginex simulator. "
            "0=disable FCUs (default), 1=FCU every test, N=FCU every Nth test per "
            "pre-allocation group."
        ),
    )
    enginex_group.addoption(
        "--enginex-max-group-size",
        dest="enginex_max_group_size",
        action="store",
        type=int,
        default=100,
        help=(
            "Maximum number of tests per xdist group. Large pre-allocation groups will be "
            "split into virtual sub-groups to improve load balancing. Default: 100."
        ),
    )


def pytest_configure(config):
    """Set the supported fixture formats and store enginex configuration."""
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
    Build group test counts during collection phase.

    This hook analyzes all collected test items to determine how many tests
    belong to each group (pre-allocation groups or xdist subgroups), enabling
    automatic client cleanup when all tests in a group are complete.
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
                    # Get group identifier from xdist marker if available
                    group_identifier = None
                    for marker in item.iter_markers("xdist_group"):
                        if hasattr(marker, "kwargs") and "name" in marker.kwargs:
                            group_identifier = marker.kwargs["name"]
                            break

                    # Fallback to pre_hash if no xdist marker (sequential execution)
                    if group_identifier is None:
                        group_identifier = test_case.pre_hash

                    group_counts[group_identifier] = group_counts.get(group_identifier, 0) + 1

        # Store on session for later retrieval by test_tracker fixture
        session._pre_alloc_group_counts = group_counts
        logger.info(f"Collected {len(group_counts)} groups with tests: {dict(group_counts)}")
    else:
        # Update tracker directly if it exists
        group_counts = {}
        for item in items:
            if hasattr(item, "callspec") and "test_case" in item.callspec.params:
                test_case = item.callspec.params["test_case"]
                if hasattr(test_case, "pre_hash"):
                    # Get group identifier from xdist marker if available
                    group_identifier = None
                    for marker in item.iter_markers("xdist_group"):
                        if hasattr(marker, "kwargs") and "name" in marker.kwargs:
                            group_identifier = marker.kwargs["name"]
                            break

                    # Fallback to pre_hash if no xdist marker (sequential execution)
                    if group_identifier is None:
                        group_identifier = test_case.pre_hash

                    group_counts[group_identifier] = group_counts.get(group_identifier, 0) + 1

        for group_identifier, count in group_counts.items():
            test_tracker.set_group_test_count(group_identifier, count)

        logger.info(f"Updated test tracker with {len(group_counts)} groups")


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


@pytest.fixture(scope="session")
def fcu_frequency_tracker(request):
    """
    Session-scoped FCU frequency tracker for enginex simulator.

    This fixture is imported from test_tracker module and configured
    with the --enginex-fcu-frequency command line option.
    """
    # Import here to avoid circular imports
    from ..helpers.test_tracker import FCUFrequencyTracker

    # Get FCU frequency from pytest config (set by command line argument)
    fcu_frequency = getattr(request.config, "enginex_fcu_frequency", 1)

    tracker = FCUFrequencyTracker(fcu_frequency=fcu_frequency)
    logger.info(f"FCU frequency tracker initialized with frequency: {fcu_frequency}")

    return tracker
