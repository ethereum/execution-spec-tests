"""Common pytest fixtures for the RLP and Engine simulators."""

import io
import json
import logging
import textwrap
import urllib
import warnings
from pathlib import Path
from typing import Dict, Generator, List, Literal, cast

import pytest
import rich
from hive.client import Client, ClientType
from hive.testing import HiveTest

from ethereum_test_base_types import Number, to_json
from ethereum_test_exceptions import ExceptionMapper
from ethereum_test_fixtures import (
    BaseFixture,
    BlockchainFixtureCommon,
)
from ethereum_test_fixtures.blockchain import SharedPreState
from ethereum_test_fixtures.consume import TestCaseIndexFile, TestCaseStream
from ethereum_test_fixtures.file import Fixtures
from ethereum_test_rpc import EthRPC
from pytest_plugins.consume.consume import FixturesSource
from pytest_plugins.consume.hive_simulators.ruleset import ruleset  # TODO: generate dynamically
from pytest_plugins.pytest_hive.hive_info import ClientFile, HiveInfo

from .exceptions import EXCEPTION_MAPPERS
from .shared_client import SharedClientRegistry
from .shared_client_proxy import SharedClientProxy
from .timing import TimingData

logger = logging.getLogger(__name__)


def pytest_sessionfinish(session, exitstatus):
    """Clean up all shared clients at the end of the test session."""
    logger.info(
        f"Session ending with status {exitstatus}, cleaning up {len(_active_shared_clients)} shared clients"
    )

    # Track uniqueness to avoid duplicate stop attempts
    processed_clients = set()

    # Clean up each active client
    for key, client_data in list(_active_shared_clients.items()):
        client_manager = client_data["client_manager"]
        client_info = client_data["client_info"]
        pre_hash = client_data["pre_hash"]
        client_type = client_data["client_type"]

        # Skip if we've already processed this client ID
        if client_info.client_id in processed_clients:
            logger.info(f"Skipping already processed client {client_info.client_id}")
            continue

        processed_clients.add(client_info.client_id)

        logger.info(
            f"Stopping shared client {client_info.client_id} (pre_hash: {pre_hash}, client: {client_type})"
        )
        try:
            # Try a direct delete call to the API
            url = f"{client_manager.base_url}/testsuite/{client_manager.suite_id}/shared-client/{client_info.client_id}"
            try:
                import requests

                response = requests.delete(url)
                logger.info(
                    f"Direct delete response: {response.status_code} - {response.text[:100]}"
                )
            except Exception as req_e:
                logger.error(f"Direct delete failed: {req_e}")
                # Fall back to manager release
                client_manager.release_client(pre_hash, client_type)
        except Exception as e:
            logger.error(f"Error stopping client {client_info.client_id}: {e}")
            logger.error("This is expected if the client was already stopped - continuing cleanup")

    # Clear the dictionary
    _active_shared_clients.clear()
    logger.info("All shared clients have been released")


def pytest_addoption(parser):
    """Hive simulator specific consume command line options."""
    consume_group = parser.getgroup(
        "consume", "Arguments related to consuming fixtures via a client"
    )
    consume_group.addoption(
        "--timing-data",
        action="store_true",
        dest="timing_data",
        default=False,
        help="Log the timing data for each test case execution.",
    )
    consume_group.addoption(
        "--disable-strict-exception-matching",
        action="store",
        dest="disable_strict_exception_matching",
        default="",
        help=(
            "Comma-separated list of client names and/or forks which should NOT use strict "
            "exception matching."
        ),
    )
    consume_group.addoption(
        "--use-shared-clients",
        action="store_true",
        dest="use_shared_clients",
        default=False,
        help=(
            "Use shared client model for more efficient test execution. Clients will be reused "
            "across test cases with the same pre-state. This can significantly improve performance "
            "by avoiding repeated client initialization for tests with the same genesis state. "
            "When enabled, tests are automatically grouped by their pre-state, and a single client "
            "instance is shared among all tests in each group."
        ),
    )


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EthRPC:
    """Initialize ethereum RPC client for the execution client under test."""
    return EthRPC(f"http://{client.ip}:8545")


@pytest.fixture(scope="function")
def hive_clients_yaml_target_filename() -> str:
    """Return the name of the target clients YAML file."""
    return "clients_eest.yaml"


@pytest.fixture(scope="function")
def hive_clients_yaml_generator_command(
    client_type: ClientType,
    client_file: ClientFile,
    hive_clients_yaml_target_filename: str,
    hive_info: HiveInfo,
) -> str:
    """Generate a shell command that creates a clients YAML file for the current client."""
    try:
        if not client_file:
            raise ValueError("No client information available - try updating hive")
        client_config = [c for c in client_file.root if c.client in client_type.name]
        if not client_config:
            raise ValueError(f"Client '{client_type.name}' not found in client file")
        try:
            yaml_content = ClientFile(root=[client_config[0]]).yaml().replace(" ", "&nbsp;")
            return f'echo "\\\n{yaml_content}" > {hive_clients_yaml_target_filename}'
        except Exception as e:
            raise ValueError(f"Failed to generate YAML: {str(e)}") from e
    except ValueError as e:
        error_message = str(e)
        warnings.warn(
            f"{error_message}. The Hive clients YAML generator command will not be available.",
            stacklevel=2,
        )

        issue_title = f"Client {client_type.name} configuration issue"
        issue_body = f"Error: {error_message}\nHive version: {hive_info.commit}\n"
        issue_url = f"https://github.com/ethereum/execution-spec-tests/issues/new?title={urllib.parse.quote(issue_title)}&body={urllib.parse.quote(issue_body)}"

        return (
            f"Error: {error_message}\n"
            f'Please <a href="{issue_url}">create an issue</a> to report this problem.'
        )


@pytest.fixture(scope="function")
def filtered_hive_options(hive_info: HiveInfo) -> List[str]:
    """Filter Hive command options to remove unwanted options."""
    logger.info("Hive info: %s", hive_info.command)

    unwanted_options = [
        "--client",  # gets overwritten: we specify a single client; the one from the test case
        "--client-file",  # gets overwritten: we'll write our own client file
        "--results-root",  # use default value instead (or you have to pass it to ./hiveview)
        "--sim.limit",  # gets overwritten: we only run the current test case id
        "--sim.parallelism",  # skip; we'll only be running a single test
    ]

    command_parts = []
    skip_next = False
    for part in hive_info.command:
        if skip_next:
            skip_next = False
            continue

        if part in unwanted_options:
            skip_next = True
            continue

        if any(part.startswith(f"{option}=") for option in unwanted_options):
            continue

        command_parts.append(part)

    return command_parts


@pytest.fixture(scope="function")
def hive_client_config_file_parameter(hive_clients_yaml_target_filename: str) -> str:
    """Return the hive client config file parameter."""
    return f"--client-file {hive_clients_yaml_target_filename}"


@pytest.fixture(scope="function")
def hive_consume_command(
    test_case: TestCaseIndexFile | TestCaseStream,
    hive_client_config_file_parameter: str,
    filtered_hive_options: List[str],
    client_type: ClientType,
) -> str:
    """Command to run the test within hive."""
    command_parts = filtered_hive_options.copy()
    command_parts.append(f"{hive_client_config_file_parameter}")
    command_parts.append(f"--client={client_type.name}")
    command_parts.append(f'--sim.limit="id:{test_case.id}"')

    return " ".join(command_parts)


@pytest.fixture(scope="function")
def hive_dev_command(
    client_type: ClientType,
    hive_client_config_file_parameter: str,
) -> str:
    """Return the command used to instantiate hive alongside the `consume` command."""
    return f"./hive --dev {hive_client_config_file_parameter} --client {client_type.name}"


@pytest.fixture(scope="function")
def eest_consume_command(
    test_suite_name: str,
    test_case: TestCaseIndexFile | TestCaseStream,
    fixture_source_flags: List[str],
) -> str:
    """Commands to run the test within EEST using a hive dev back-end."""
    flags = " ".join(fixture_source_flags)
    return (
        f"uv run consume {test_suite_name.split('-')[-1]} "
        f'{flags} --sim.limit="id:{test_case.id}" -v -s'
    )


# Global dictionary to track active shared clients across tests
# This allows us to maintain clients without reference counting problems
_active_shared_clients = {}


@pytest.fixture(scope="function")
def test_case_description(
    fixture: BaseFixture,
    test_case: TestCaseIndexFile | TestCaseStream,
    hive_clients_yaml_generator_command: str,
    hive_consume_command: str,
    hive_dev_command: str,
    eest_consume_command: str,
) -> str:
    """Create the description of the current blockchain fixture test case."""
    test_url = fixture.info.get("url", "")

    if "description" not in fixture.info or fixture.info["description"] is None:
        test_docstring = "No documentation available."
    else:
        # this prefix was included in the fixture description field for fixtures <= v4.3.0
        test_docstring = fixture.info["description"].replace("Test function documentation:\n", "")  # type: ignore

    description = textwrap.dedent(f"""
        <b>Test Details</b>
        <code>{test_case.id}</code>
        {f'<a href="{test_url}">[source]</a>' if test_url else ""}

        {test_docstring}

        <b>Run This Test Locally:</b>
        To run this test in <a href="https://github.com/ethereum/hive">hive</a></i>:
        <code>{hive_clients_yaml_generator_command}
            {hive_consume_command}</code>

        <b>Advanced: Run the test against a hive developer backend using EEST's <code>consume</code> command</b>
        Create the client YAML file, as above, then:
        1. Start hive in dev mode: <code>{hive_dev_command}</code>
        2. In the EEST repository root: <code>{eest_consume_command}</code>
    """)  # noqa: E501

    description = description.strip()
    description = description.replace("\n", "<br/>")
    return description


@pytest.fixture(scope="function", autouse=True)
def total_timing_data(request) -> Generator[TimingData, None, None]:
    """Record timing data for various stages of executing test case."""
    with TimingData("Total (seconds)") as total_timing_data:
        yield total_timing_data
    if request.config.getoption("timing_data"):
        rich.print(f"\n{total_timing_data.formatted()}")
    if hasattr(request.node, "rep_call"):  # make available for test reports
        request.node.rep_call.timings = total_timing_data


# Module-level cache for client genesis and test counts
_client_genesis_cache = {}
_test_count_cache = {}


def create_client_genesis(
    fixture: BlockchainFixtureCommon,
    pre_hash: int = None,
    use_shared_client: bool = False,
    shared_pre_alloc_path: Path = None,
) -> tuple[dict, int]:
    """
    Convert the fixture genesis block header and pre-state to a client genesis state.

    For shared client mode, we use a cache to avoid repeated processing of the same genesis.
    This prevents issues with repeated conversion of the allocation dict.

    Args:
        fixture: The fixture containing genesis and pre-state data
        pre_hash: Optional hash of the pre-state for caching (only used with use_shared_client)
        use_shared_client: Whether to use shared client mode with caching
        shared_pre_alloc_path: Optional path to a shared pre-allocation file

    Returns:
        tuple: (genesis dict, test count for this pre_hash group)
    """
    test_count = 0
    # If using shared client mode with a valid pre_hash, check the cache
    if use_shared_client and pre_hash is not None:
        if pre_hash in _client_genesis_cache:
            logger.info(f"Using cached genesis for pre_hash {pre_hash}")
            cached_test_count = _test_count_cache.get(pre_hash, 0)
            return _client_genesis_cache[pre_hash], cached_test_count

        # Try to load from shared_pre_alloc_path first (if provided explicitly)
        if shared_pre_alloc_path is not None and shared_pre_alloc_path.exists():
            try:
                logger.info(f"Loading shared pre-allocation from {shared_pre_alloc_path}")

                # Use the SharedPreState pydantic model to load the file
                try:
                    # First try loading with the model directly, expecting 'root' field
                    shared_data = SharedPreState.model_validate_json(
                        shared_pre_alloc_path.read_text()
                    )
                    logger.info(f"Loaded shared pre-allocation using standard model")
                except Exception as load_error:
                    # If that fails, try loading as raw JSON and convert to the expected format
                    logger.info(
                        f"Standard model loading failed: {load_error}, trying alternative format"
                    )
                    try:
                        raw_data = json.loads(shared_pre_alloc_path.read_text())
                        # Check if this is a raw dictionary format without the 'root' wrapper
                        if isinstance(raw_data, dict) and all(
                            k.isdigit() for k in raw_data.keys()
                        ):
                            # Create a SharedPreState using our helper method
                            shared_data = SharedPreState.from_raw_dict(raw_data)
                            logger.info(
                                f"Created SharedPreState from raw data with {len(shared_data.root)} entries"
                            )
                        else:
                            raise ValueError(
                                f"Couldn't parse shared pre-allocation file: unknown format"
                            )
                    except Exception as e:
                        logger.error(f"Failed to parse shared pre-allocation file: {e}")
                        raise

                # Convert pre_hash to string to match the keys in the JSON file
                # pre_hash_str = str(pre_hash)

                # Check if this pre_hash exists in the shared data
                if pre_hash in shared_data.root:
                    logger.info(f"Found shared pre-allocation for pre_hash {pre_hash}")
                    shared_entry = shared_data.root[pre_hash]

                    # Extract test count from fixture_names
                    test_count = len(shared_entry.fixture_names)
                    logger.info(f"Pre-hash {pre_hash} has {test_count} tests in fixture_names")

                    # Create genesis from the genesisBlockHeader field
                    genesis = to_json(fixture.genesis)

                    # Use the pre-allocation from shared data
                    if shared_entry.pre is not None:
                        pre_data = to_json(shared_entry.pre)
                        # NOTE: nethermind requires account keys without '0x' prefix
                        logger.info(f"Using pre-allocation with {len(pre_data)} accounts")
                        genesis["alloc"] = {k.replace("0x", ""): v for k, v in pre_data.items()}

                        # Cache this genesis and test count for future use
                        _client_genesis_cache[pre_hash] = genesis
                        _test_count_cache[pre_hash] = test_count
                        logger.info(f"Using shared pre-allocation for pre_hash {pre_hash}")
                        return genesis, test_count
                    else:
                        logger.warning(
                            f"Pre-allocation is None in shared data for pre_hash {pre_hash}"
                        )
                else:
                    logger.warning(f"Pre-hash {pre_hash} not found in shared data")
                    logger.info(f"Available pre-hashes: {list(shared_data.root.keys())[:5]}...")
            except Exception as e:
                logger.warning(f"Failed to load shared pre-allocation: {e}")
                # Continue with checking shared_pre_state.json

    # Process the genesis and allocation
    genesis = to_json(fixture.genesis)

    # In non-shared client mode, we might not have a pre-allocation
    if fixture.pre is None:
        logger.warning(f"Pre-allocation is None for fixture, using empty allocation")
        genesis["alloc"] = {}
    else:
        alloc = to_json(fixture.pre)

        # Handle different types of allocation data
        if isinstance(alloc, dict):
            # NOTE: nethermind requires account keys without '0x' prefix
            genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
        elif isinstance(alloc, str):
            # If we got a string, assume it's already formatted correctly
            try:
                # Try to parse it just to validate it's valid JSON
                json.loads(alloc)
                genesis["alloc"] = alloc
            except json.JSONDecodeError:
                # If it's not valid JSON, log an error
                logger.error(f"Invalid allocation string: {alloc}")
                raise ValueError(f"Invalid allocation string: {alloc}")
        elif alloc is None:
            # Handle None case - use empty allocation
            logger.warning(f"Allocation is None, using empty allocation")
            genesis["alloc"] = {}
        else:
            # Something unexpected
            genesis["alloc"] = alloc
            logger.warning(f"Unexpected allocation type: {type(alloc)}")

    # Cache the result in shared client mode
    if use_shared_client and pre_hash is not None:
        _client_genesis_cache[pre_hash] = genesis

    return genesis, test_count


@pytest.fixture(scope="function")
def check_live_port(test_suite_name: str) -> Literal[8545, 8551]:
    """Port used by hive to check for liveness of the client."""
    if test_suite_name == "eest/consume-rlp":
        return 8545
    elif test_suite_name == "eest/consume-engine":
        return 8551
    raise ValueError(
        f"Unexpected test suite name '{test_suite_name}' while setting HIVE_CHECK_LIVE_PORT."
    )


def create_environment(
    fixture: BlockchainFixtureCommon,
    check_live_port: Literal[8545, 8551],
) -> dict:
    """
    Define the environment variables that hive will use to start the client.

    Args:
        fixture: The fixture containing chain configuration
        check_live_port: Port to check for client liveness (8545 for RLP, 8551 for Engine)

    Returns:
        dict: Environment variables for client configuration
    """
    assert fixture.fork in ruleset, f"fork '{fixture.fork}' missing in hive ruleset"

    # Always ensure we're in PoS mode for the Engine API
    environment = {
        "HIVE_CHAIN_ID": str(Number(fixture.config.chain_id)),
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        "HIVE_CHECK_LIVE_PORT": str(check_live_port),
        # Required to avoid SYNCING when using Engine API
        **{k: f"{v:d}" for k, v in ruleset[fixture.fork].items()},
    }

    # For Engine API, explicitly set PoS mode
    if check_live_port == 8551:
        # These settings are needed for the Engine API to work properly
        environment["HIVE_FORK_MERGE"] = "0"
        environment["HIVE_TERMINAL_TOTAL_DIFFICULTY"] = "0"

    # Log the environment for debugging
    logger.info(f"Client environment: {environment}")

    return environment


def create_buffered_genesis(genesis: dict) -> io.BufferedReader:
    """
    Create a buffered reader for a genesis configuration.

    Args:
        genesis: The genesis configuration dict

    Returns:
        io.BufferedReader: A buffered reader containing the genesis JSON
    """
    # Ensure the alloc field is properly preserved
    if "alloc" in genesis and isinstance(genesis["alloc"], dict):
        alloc_count = len(genesis["alloc"])
        logger.info(f"Creating buffered genesis with {alloc_count} accounts in alloc")
        if alloc_count > 0:
            logger.info(f"Sample account: {next(iter(genesis['alloc']))}")
    else:
        logger.warning(f"No alloc dictionary found in genesis")

    # Create the buffered genesis
    genesis_json = json.dumps(genesis)
    logger.info(f"Genesis JSON size: {len(genesis_json)} bytes")
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))


@pytest.fixture(scope="session")
def client_exception_mapper_cache():
    """Cache for exception mappers by client type."""
    return {}


@pytest.fixture(scope="function")
def client_exception_mapper(
    client_type: ClientType, client_exception_mapper_cache
) -> ExceptionMapper | None:
    """Return the exception mapper for the client type, with caching."""
    if client_type.name not in client_exception_mapper_cache:
        for client in EXCEPTION_MAPPERS:
            if client in client_type.name:
                client_exception_mapper_cache[client_type.name] = EXCEPTION_MAPPERS[client]
                break
        else:
            client_exception_mapper_cache[client_type.name] = None

    return client_exception_mapper_cache[client_type.name]


@pytest.fixture(scope="session")
def disable_strict_exception_matching(request: pytest.FixtureRequest) -> List[str]:
    """Return the list of clients or forks that should NOT use strict exception matching."""
    config_string = request.config.getoption("disable_strict_exception_matching")
    return config_string.split(",") if config_string else []


@pytest.fixture(scope="function")
def client_strict_exception_matching(
    client_type: ClientType,
    disable_strict_exception_matching: List[str],
) -> bool:
    """Return True if the client type should use strict exception matching."""
    return not any(
        client.lower() in client_type.name.lower() for client in disable_strict_exception_matching
    )


@pytest.fixture(scope="function")
def fork_strict_exception_matching(
    fixture: BlockchainFixtureCommon,
    disable_strict_exception_matching: List[str],
) -> bool:
    """Return True if the fork should use strict exception matching."""
    # NOTE: `in` makes it easier for transition forks ("Prague" in "CancunToPragueAtTime15k")
    return not any(
        fork.lower() in fixture.fork.lower() for fork in disable_strict_exception_matching
    )


@pytest.fixture(scope="function")
def strict_exception_matching(
    client_strict_exception_matching: bool,
    fork_strict_exception_matching: bool,
) -> bool:
    """Return True if the test should use strict exception matching."""
    return client_strict_exception_matching and fork_strict_exception_matching


@pytest.fixture(scope="session")
def shared_client_registry(request) -> SharedClientRegistry:
    """
    Get the global shared client registry.

    This fixture provides access to the singleton registry without
    depending on other fixtures, avoiding scope conflicts.
    """
    registry = SharedClientRegistry.get_instance()

    def cleanup_shared_clients():
        """Release all shared clients at the end of the test session."""
        registry_instance = SharedClientRegistry.get_instance()
        logger.info("Cleaning up all shared clients at session end")
        # For each manager in the registry
        for manager_key, manager in registry_instance.managers.items():
            # For each client managed by the manager
            for client_key, client_info in list(manager.clients.items()):
                pre_hash, client_type = client_key
                logger.info(
                    f"Stopping shared client {client_info.client_id} for pre-hash {pre_hash} and client {client_type}"
                )
                manager.release_client(pre_hash, client_type)
        logger.info("All shared clients have been released")

    # Add session finalizer
    request.addfinalizer(cleanup_shared_clients)
    return registry


def get_client_manager_for_suite(
    simulator_url: str, suite_id: str, registry: SharedClientRegistry
):
    """
    Get the shared client manager for a test suite.

    This is a helper function rather than a fixture to avoid scope issues.

    Args:
        simulator_url: URL of the simulator
        suite_id: ID of the test suite
        registry: Shared client registry

    Returns:
        The shared client manager for the suite
    """
    logger.info(f"Getting client manager for URL: {simulator_url} and suite ID: {suite_id}")
    return registry.get_manager(simulator_url, suite_id)


@pytest.fixture(scope="function")
def use_shared_client(request) -> bool:
    """
    Determine whether to use the shared client model based on command line option.

    Uses the --use-shared-clients flag. For consistency with the option name,
    this fixture should ideally be renamed to use_shared_clients, but keeping
    it as use_shared_client for backward compatibility.
    """
    return request.config.getoption("use_shared_clients")


@pytest.fixture(scope="function")
def pre_hash(fixture: BlockchainFixtureCommon) -> int | None:
    """
    Compute a hash value for the pre-state of a blockchain fixture.

    This hash is used to identify fixtures with the same pre-state,
    which can share the same client instance.
    """
    return fixture.pre_hash


@pytest.fixture(scope="function")
def client(
    hive_test: HiveTest,
    client_files: dict,  # configured within: rlp/conftest.py & engine/conftest.py
    client_type: ClientType,
    total_timing_data: TimingData,
    use_shared_client: bool,
    pre_hash: int,
    shared_client_registry,  # The shared client registry (session-scoped)
    test_suite,  # We need the test suite to get its ID
    test_suite_name: str,
    test_suite_description: str,
    fixture: BlockchainFixtureCommon,
    check_live_port: Literal[8545, 8551],
    request,
) -> Generator[Client, None, None]:
    """
    Initialize the client with the appropriate files and environment variables.

    If use_shared_client is True, this will use the shared client model,
    which allows multiple tests with the same pre-state to share a client.
    This implementation uses the new Hive shared client API.
    """
    # Create a shared pre-state path if using shared clients
    shared_pre_alloc_path = None
    if use_shared_client:
        # Check for fixtures_source to load shared pre-state
        fixtures_source = request.config.getoption("fixtures_source", None)
        if fixtures_source:
            # First try tmp directory
            shared_pre_alloc_path = Path(
                "/home/dtopz/code/github/new/execution-spec-tests/tmp/shared_pre_alloc.json"
            )
            if not shared_pre_alloc_path.exists():
                # Try fixtures_source directory
                shared_pre_alloc_path = Path(fixtures_source) / "shared_pre_alloc.json"

            # Debug log to show what we're using
            if shared_pre_alloc_path.exists():
                logger.info(f"Found shared_pre_alloc.json at {shared_pre_alloc_path}")
            else:
                logger.warning(f"Could not find shared_pre_alloc.json at {shared_pre_alloc_path}")

    # Generate genesis and environment using helper functions
    genesis, test_count = create_client_genesis(
        fixture=fixture,
        pre_hash=pre_hash if use_shared_client else None,
        use_shared_client=use_shared_client,
        shared_pre_alloc_path=shared_pre_alloc_path,
    )

    # Debug log the genesis config
    if "alloc" in genesis and isinstance(genesis["alloc"], dict):
        logger.info(f"Generated genesis with {len(genesis['alloc'])} accounts")
    else:
        logger.warning("Generated genesis has no allocation dictionary")

    environment = create_environment(fixture, check_live_port)

    if not use_shared_client:
        # Traditional client model - create a new client for each test case
        logger.info(f"Starting individual client ({client_type.name})...")
        with total_timing_data.time("Start client"):
            client = hive_test.start_client(
                client_type=client_type,
                environment=environment,
                files={**client_files, "/genesis.json": create_buffered_genesis(genesis)},
            )
        error_message = (
            f"Unable to connect to the client container ({client_type.name}) via Hive during test "
            "setup. Check the client or Hive server logs for more information."
        )
        assert client is not None, error_message
        logger.info(f"Client ({client_type.name}) ready!")
        yield client
        logger.info(f"Stopping client ({client_type.name})...")
        with total_timing_data.time("Stop client"):
            client.stop()
        logger.info(f"Client ({client_type.name}) stopped!")
    else:
        # Shared client model using the new Hive shared client API
        logger.info(f"Using shared client model for pre_hash {pre_hash}")

        # Get the shared client registry
        registry = shared_client_registry

        # Get the simulator URL from the config
        simulator_url = request.config.hive_simulator_url

        # Create a unique test suite for this pre_hash group
        # Using the pre_hash in the suite name ensures 1-to-1 mapping
        suite_name = f"{test_suite_name}_pre{pre_hash}"
        suite_description = f"{test_suite_description} (pre_hash: {pre_hash})"

        # First check if we already have a manager for this pre_hash
        # We need to look through all managers to find one handling this pre_hash
        client_manager = None
        shared_test_suite = None
        suite_id = None

        for manager_key, manager in registry.managers.items():
            if pre_hash in manager.test_suites:
                # Found a manager already handling this pre_hash
                client_manager = manager
                shared_test_suite = manager.test_suites[pre_hash]
                suite_id = shared_test_suite.id
                logger.info(f"Found existing suite {shared_test_suite.id} for pre_hash {pre_hash}")
                break

        if client_manager is None:
            # No existing manager for this pre_hash, create a new suite
            with total_timing_data.time("Create shared client test suite"):
                simulator = request.config.hive_simulator
                shared_test_suite = simulator.start_suite(
                    name=suite_name,
                    description=suite_description,
                )
                logger.info(f"Created test suite {shared_test_suite.id} for pre_hash {pre_hash}")

                # Use the suite ID to get/create the manager
                suite_id = shared_test_suite.id
                client_manager = get_client_manager_for_suite(simulator_url, suite_id, registry)

        # Set the test count and suite for this pre_hash group
        if test_count > 0:
            client_manager.set_test_count(pre_hash, test_count)
            client_manager.set_test_suite(pre_hash, shared_test_suite)

        # logger.info(f"gensis: {genesis}")
        # genesis["alloc"] = {}  # Remove alloc for shared client
        with total_timing_data.time("Get or start shared client"):
            # Use the client manager to get or start a shared client
            client_info = client_manager.start_client(
                pre_hash=pre_hash,
                client_type=client_type.name,
                environment=environment,
                files={**client_files, "/genesis.json": create_buffered_genesis(genesis)},
            )

        if client_info is None:
            pytest.fail(f"Failed to start or get shared client for pre_hash {pre_hash}")

        # Create a proxy that adapts the SharedClient to the standard Client interface
        client_proxy = SharedClientProxy(
            manager=client_manager,
            pre_hash=pre_hash,
            client_type=client_type.name,
            client_id=client_info.client_id,
            ip=client_info.ip,
        )

        logger.info(f"Shared client ready (ID: {client_info.client_id}, pre_hash: {pre_hash})")

        # Record starting log offset before running the test
        client_manager.get_log_offset(pre_hash, client_type.name)

        yield client_proxy

        # Add this client to our global tracking dictionary
        client_key = f"{simulator_url}:{suite_id}:{pre_hash}:{client_type.name}"
        if client_key not in _active_shared_clients:
            _active_shared_clients[client_key] = {
                "client_info": client_info,
                "client_manager": client_manager,
                "pre_hash": pre_hash,
                "client_type": client_type.name,
                "ref_count": 0,
            }

        # Increment reference count
        _active_shared_clients[client_key]["ref_count"] += 1

        logger.info(
            f"Keeping shared client (ID: {client_info.client_id}, pre_hash: {pre_hash}) for reuse"
        )
        logger.info(
            f"Current active clients: {len(_active_shared_clients)}, client {client_key} ref count: {_active_shared_clients[client_key]['ref_count']}"
        )

        # Mark this test as completed for the pre_hash group
        client_manager.complete_test(pre_hash)

        # NOTE: Not releasing client here - we want to keep references across test functions!


@pytest.fixture(scope="function", autouse=True)
def timing_data(
    total_timing_data: TimingData, client: Client
) -> Generator[TimingData, None, None]:
    """Record timing data for the main execution of the test case."""
    with total_timing_data.time("Test case execution") as timing_data:
        yield timing_data


class FixturesDict(Dict[Path, Fixtures]):
    """
    A dictionary caches loaded fixture files to avoid reloading the same file
    multiple times.
    """

    def __init__(self) -> None:
        """Initialize the dictionary that caches loaded fixture files."""
        self._fixtures: Dict[Path, Fixtures] = {}

    def __getitem__(self, key: Path) -> Fixtures:
        """Return the fixtures from the index file, if not found, load from disk."""
        assert key.is_file(), f"Expected a file path, got '{key}'"
        if key not in self._fixtures:
            self._fixtures[key] = Fixtures.model_validate_json(key.read_text())
        return self._fixtures[key]


@pytest.fixture(scope="session")
def fixture_file_loader() -> Dict[Path, Fixtures]:
    """Return a singleton dictionary that caches loaded fixture files used in all tests."""
    return FixturesDict()


@pytest.fixture(scope="function")
def fixture(
    fixtures_source: FixturesSource,
    fixture_file_loader: Dict[Path, Fixtures],
    test_case: TestCaseIndexFile | TestCaseStream,
) -> BaseFixture:
    """
    Load the fixture from a file or from stream in any of the supported
    fixture formats.

    The fixture is either already available within the test case (if consume
    is taking input on stdin) or loaded from the fixture json file if taking
    input from disk (fixture directory with index file).
    """
    fixture: BaseFixture
    if fixtures_source.is_stdin:
        assert isinstance(test_case, TestCaseStream), "Expected a stream test case"
        fixture = test_case.fixture
    else:
        assert isinstance(test_case, TestCaseIndexFile), "Expected an index file test case"
        fixtures_file_path = fixtures_source.path / test_case.json_path
        fixtures: Fixtures = fixture_file_loader[fixtures_file_path]
        fixture = fixtures[test_case.id]
    assert isinstance(fixture, test_case.format), (
        f"Expected a {test_case.format.format_name} test fixture"
    )
    return fixture
