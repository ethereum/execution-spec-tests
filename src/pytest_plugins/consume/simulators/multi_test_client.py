"""Common pytest fixtures for simulators with multi-test client architecture."""

import io
import json
import logging
from typing import Dict, Generator, Mapping, cast

import pytest
from hive.client import Client, ClientType
from hive.testing import HiveTest, HiveTestSuite

from ethereum_test_base_types import to_json
from ethereum_test_fixtures import BlockchainEngineXFixture
from ethereum_test_fixtures.blockchain import FixtureHeader
from ethereum_test_fixtures.pre_alloc_groups import PreAllocGroup
from pytest_plugins.consume.consume import FixturesSource
from pytest_plugins.consume.simulators.helpers.ruleset import (
    ruleset,  # TODO: generate dynamically
)
from pytest_plugins.filler.fixture_output import FixtureOutput

from .helpers.client_wrapper import (
    MultiTestClientManager,
    get_group_identifier_from_request,
)
from .helpers.timing import TimingData

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def pre_alloc_group_cache() -> Dict[str, PreAllocGroup]:
    """Cache for pre-allocation groups to avoid reloading from disk."""
    return {}


@pytest.fixture(scope="function")
def pre_alloc_group(
    fixture: BlockchainEngineXFixture,
    fixtures_source: FixturesSource,
    pre_alloc_group_cache: Dict[str, PreAllocGroup],
) -> PreAllocGroup:
    """Load the pre-allocation group for the current test case."""
    pre_hash = fixture.pre_hash

    # Check cache first
    if pre_hash in pre_alloc_group_cache:
        return pre_alloc_group_cache[pre_hash]

    # Load from disk
    if fixtures_source.is_stdin:
        raise ValueError("Pre-allocation groups require file-based fixture input.")

    # Look for pre-allocation group file using FixtureOutput path structure
    fixture_output = FixtureOutput(output_path=fixtures_source.path)
    pre_alloc_path = fixture_output.pre_alloc_groups_folder_path / f"{pre_hash}.json"
    if not pre_alloc_path.exists():
        raise FileNotFoundError(f"Pre-allocation group file not found: {pre_alloc_path}")

    # Load and cache
    with open(pre_alloc_path) as f:
        pre_alloc_group_obj = PreAllocGroup.model_validate_json(f.read())

    pre_alloc_group_cache[pre_hash] = pre_alloc_group_obj
    return pre_alloc_group_obj


def create_environment(pre_alloc_group: PreAllocGroup, check_live_port: int) -> dict:
    """Define environment using PreAllocGroup data."""
    fork = pre_alloc_group.fork
    assert fork in ruleset, f"fork '{fork}' missing in hive ruleset"
    return {
        "HIVE_CHAIN_ID": "1",  # TODO: Environment doesn't have chain_id - see work_in_progress.md
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        "HIVE_CHECK_LIVE_PORT": str(check_live_port),
        **{k: f"{v:d}" for k, v in ruleset[fork].items()},
    }


def client_files(pre_alloc_group: PreAllocGroup) -> Mapping[str, io.BufferedReader]:
    """Define the files that hive will start the client with."""
    genesis = to_json(pre_alloc_group.genesis)  # type: ignore
    alloc = to_json(pre_alloc_group.pre)

    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}

    genesis_json = json.dumps(genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    buffered_genesis = io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))

    files = {}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="session")
def multi_test_client_manager() -> Generator[MultiTestClientManager, None, None]:
    """Provide singleton MultiTestClientManager with session cleanup."""
    manager = MultiTestClientManager()
    try:
        yield manager
    finally:
        logger.info("Cleaning up multi-test clients at session end...")
        manager.stop_all_clients()


@pytest.fixture(scope="function")
def genesis_header(pre_alloc_group: PreAllocGroup) -> FixtureHeader:
    """Provide the genesis header from the pre-allocation group."""
    return pre_alloc_group.genesis  # type: ignore


@pytest.fixture(scope="function")
def client(
    test_suite: HiveTestSuite,
    hive_test: HiveTest,
    client_type: ClientType,
    total_timing_data: TimingData,
    fixture: BlockchainEngineXFixture,
    pre_alloc_group: PreAllocGroup,
    multi_test_client_manager: MultiTestClientManager,
    fixtures_source: FixturesSource,
    pre_alloc_group_test_tracker,
    request,
) -> Generator[Client, None, None]:
    """Initialize or reuse multi-test client for the test group."""
    logger.info("🔥 MULTI-TEST CLIENT FIXTURE CALLED - Using multi-test client architecture!")
    pre_hash = fixture.pre_hash
    test_id = request.node.nodeid

    # Determine the appropriate group identifier for this test
    group_identifier = get_group_identifier_from_request(request, pre_hash)
    logger.info(f"Using group identifier: {group_identifier} (pre_hash: {pre_hash})")

    # Set pre-alloc path in manager if not already set
    if multi_test_client_manager.pre_alloc_path is None:
        fixture_output = FixtureOutput(output_path=fixtures_source.path)
        multi_test_client_manager.set_pre_alloc_path(fixture_output.pre_alloc_groups_folder_path)

    # Set test tracker in manager if not already set
    if multi_test_client_manager.test_tracker is None:
        multi_test_client_manager.set_test_tracker(pre_alloc_group_test_tracker)

    # Check for existing client
    existing_client = multi_test_client_manager.get_client_for_test(group_identifier, test_id)
    if existing_client is not None:
        logger.info(f"Reusing multi-test client for group {group_identifier}")
        hive_test.register_shared_client(existing_client)
        try:
            yield existing_client
        finally:
            # Mark test as completed when fixture teardown occurs
            multi_test_client_manager.mark_test_completed(group_identifier, test_id)
        return

    # Start new multi-test client
    logger.info(f"Starting multi-test client for group {group_identifier}")

    with total_timing_data.time("Start multi-test client"):
        hive_client = test_suite.start_client(
            client_type=client_type,
            environment=create_environment(pre_alloc_group, 8551),
            files=client_files(pre_alloc_group),
        )

    assert hive_client is not None, (
        f"Failed to start multi-test client for group {group_identifier}"
    )

    # Register with manager
    multi_test_client = multi_test_client_manager.get_or_create_multi_test_client(
        group_identifier=group_identifier,
        client_type=client_type,
    )
    multi_test_client.set_client(hive_client)
    hive_test.register_shared_client(hive_client)

    logger.info(f"Multi-test client ready for group {group_identifier}")
    try:
        yield hive_client
    finally:
        # Mark test as completed when fixture teardown occurs
        multi_test_client_manager.mark_test_completed(group_identifier, test_id)
