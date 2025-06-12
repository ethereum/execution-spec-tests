"""Pytest configuration and fixtures for the engine reorg simulator."""

import io
import json
import logging
from typing import Dict, Generator, Mapping, cast

import pytest
from hive.client import Client, ClientType
from hive.testing import HiveTestSuite

from ethereum_test_base_types import to_json
from ethereum_test_fixtures import BlockchainEngineReorgFixture
from ethereum_test_fixtures.shared_alloc import SharedPreStateGroup
from pytest_plugins.consume.consume import FixturesSource
from pytest_plugins.filler.fixture_output import FixtureOutput
from pytest_plugins.consume.hive_simulators.ruleset import ruleset
from pytest_plugins.consume.hive_simulators.timing import TimingData

from ..client_wrapper import ReorgClientManager

logger = logging.getLogger(__name__)


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
    return (
        "Execute blockchain tests against clients using the Engine API and shared clients "
        "using engine reorg fixtures."
    )


@pytest.fixture(scope="session")
def shared_pre_state_cache() -> Dict[str, SharedPreStateGroup]:
    """Cache for shared pre-state groups to avoid reloading from disk."""
    return {}


@pytest.fixture(scope="function")
def shared_pre_state_group(
    fixture: BlockchainEngineReorgFixture,
    fixtures_source: FixturesSource,
    shared_pre_state_cache: Dict[str, SharedPreStateGroup],
) -> SharedPreStateGroup:
    """Load the shared pre-state group for the current test case."""
    pre_hash = fixture.pre_hash

    # Check cache first
    if pre_hash in shared_pre_state_cache:
        return shared_pre_state_cache[pre_hash]

    # Load from disk
    if fixtures_source.is_stdin:
        raise ValueError("Shared pre-state groups require file-based fixture input.")

    # Look for shared pre-allocation file using FixtureOutput path structure
    fixture_output = FixtureOutput(output_path=fixtures_source.path)
    shared_alloc_path = fixture_output.shared_pre_alloc_folder_path / f"{pre_hash}.json"
    if not shared_alloc_path.exists():
        raise FileNotFoundError(f"Shared pre-allocation file not found: {shared_alloc_path}")

    # Load and cache
    with open(shared_alloc_path) as f:
        shared_group = SharedPreStateGroup.model_validate_json(f.read())

    shared_pre_state_cache[pre_hash] = shared_group
    return shared_group



@pytest.fixture(scope="function")
def environment(shared_pre_state_group: SharedPreStateGroup, check_live_port: int) -> dict:
    """Define environment using SharedPreStateGroup data."""
    fork = shared_pre_state_group.fork
    assert fork in ruleset, f"fork '{fork}' missing in hive ruleset"
    return {
        "HIVE_CHAIN_ID": "1",  # TODO: Environment doesn't have chain_id - see work_in_progress.md
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        "HIVE_CHECK_LIVE_PORT": str(check_live_port),
        **{k: f"{v:d}" for k, v in ruleset[fork].items()},
    }


@pytest.fixture(scope="function")
def buffered_genesis(client_genesis: dict) -> io.BufferedReader:
    """Create a buffered reader for the genesis block header of the current test fixture."""
    genesis_json = json.dumps(client_genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))


@pytest.fixture(scope="function")
def client_files(buffered_genesis: io.BufferedReader) -> Mapping[str, io.BufferedReader]:
    """Define the files that hive will start the client with."""
    files = {}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="function")
def genesis_header(shared_pre_state_group: SharedPreStateGroup):
    """Get the genesis header from the shared pre-state group."""
    return shared_pre_state_group.genesis


@pytest.fixture(scope="session")
def reorg_client_manager() -> Generator[ReorgClientManager, None, None]:
    """Provide singleton ReorgClientManager with session cleanup."""
    manager = ReorgClientManager()
    try:
        yield manager
    finally:
        logger.info("Cleaning up shared clients at session end...")
        manager.stop_all_clients()


@pytest.fixture(scope="function")
def reorg_client(
    test_suite: HiveTestSuite,
    client_files: dict,
    environment: dict,
    client_type: ClientType,
    total_timing_data: TimingData,
    fixture: BlockchainEngineReorgFixture,
    shared_pre_state_group: SharedPreStateGroup,
    reorg_client_manager: ReorgClientManager,
    fixtures_source: FixturesSource,
) -> Generator[Client, None, None]:
    """Initialize or reuse shared client for the test group."""
    logger.info("🔥 REORG CLIENT FIXTURE CALLED - Using shared client architecture!")
    pre_hash = fixture.pre_hash

    # Set pre-alloc path in manager if not already set
    if reorg_client_manager.pre_alloc_path is None:
        fixture_output = FixtureOutput(output_path=fixtures_source.path)
        reorg_client_manager.set_pre_alloc_path(fixture_output.shared_pre_alloc_folder_path)

    # Check for existing client
    existing_client = reorg_client_manager.get_client_for_test(pre_hash)
    if existing_client is not None:
        logger.info(f"Reusing shared client for preHash: {pre_hash}")
        yield existing_client
        return

    # Start new shared client
    logger.info(f"Starting shared client for preHash: {pre_hash}")

    with total_timing_data.time("Start shared client"):
        hive_client = test_suite.start_client(
            client_type=client_type,
            environment=environment,
            files=client_files,
        )

    assert hive_client is not None, f"Failed to start shared client for preHash: {pre_hash}"

    # Register with manager
    reorg_client = reorg_client_manager.get_or_create_reorg_client(
        pre_hash=pre_hash,
        client_type=client_type,
    )
    reorg_client.set_client(hive_client)

    logger.info(f"Shared client ready for preHash: {pre_hash}")
    yield hive_client
