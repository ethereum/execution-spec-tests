"""
Pytest fixtures for the `consume engine` simulator.

Configures the hive back-end & EL clients for each individual test execution.
"""

import io
import json
from pathlib import Path
from typing import Generator, Mapping, cast

import pytest
from hive.client import Client, ClientType
from hive.testing import HiveTest

from ethereum_test_base_types.json import to_json
from ethereum_test_fixtures import BlockchainHiveFixture
from ethereum_test_fixtures.consume import TestCaseIndexFile, TestCaseStream
from ethereum_test_fixtures.file import BlockchainHiveFixtures
from ethereum_test_tools.rpc import EngineRPC, EthRPC
from pytest_plugins.consume.common import JsonSource
from pytest_plugins.consume.hive_simulators.ruleset import ruleset  # TODO: generate dynamically

TestCase = TestCaseIndexFile | TestCaseStream


@pytest.fixture(scope="session")
def test_suite_name() -> str:
    """
    The name of the hive test suite used in this simulator.
    """
    return "eest-engine"


@pytest.fixture(scope="session")
def test_suite_description() -> str:
    """
    The description of the hive test suite used in this simulator.
    """
    return "Execute blockchain tests by against clients using the `engine_newPayloadVX` method."


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    return EthRPC(ip=client.ip)


@pytest.fixture(scope="function")
def engine_rpc(client: Client) -> EngineRPC:
    """
    Initialize engine RPC client for the execution client under test.
    """
    return EngineRPC(ip=client.ip)


@pytest.fixture(scope="function")
def blockchain_fixture(fixture_source: JsonSource, test_case: TestCase) -> BlockchainHiveFixture:
    """
    Create the blockchain engine fixture pydantic model for the current test case.

    The fixture is either already available within the test case (if consume
    is taking input on stdin) or loaded from the fixture json file if taking
    input from disk (fixture directory with index file).
    """
    if fixture_source == "stdin":
        assert isinstance(test_case, TestCaseStream), "Expected a stream test case"
        assert isinstance(
            test_case.fixture, BlockchainHiveFixture
        ), "Expected a blockchain engine test fixture"
        fixture = test_case.fixture
    else:
        assert isinstance(test_case, TestCaseIndexFile), "Expected an index file test case"
        # TODO: Optimize, json files will be loaded multiple times. This pytest fixture
        # is executed per test case, and a fixture json will contain multiple test cases.
        fixtures = BlockchainHiveFixtures.from_file(Path(fixture_source) / test_case.json_path)
        fixture = fixtures[test_case.id]
    return fixture


@pytest.fixture(scope="function")
def fixture_description(blockchain_fixture: BlockchainHiveFixture, test_case: TestCase) -> str:
    """
    Create the description of the current blockchain engine fixture test case.
    """
    description = f"Test id: {test_case.id}"
    if "url" in blockchain_fixture.info:
        description += f"\n\nTest source: {blockchain_fixture.info['url']}"
    if "description" not in blockchain_fixture.info:
        description += "\n\nNo description field provided in the fixture's 'info' section."
    else:
        description += f"\n\n{blockchain_fixture.info['description']}"
    return description


@pytest.fixture(scope="function")
def client_genesis(blockchain_fixture: BlockchainHiveFixture) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(blockchain_fixture.genesis)
    alloc = to_json(blockchain_fixture.pre)
    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
    return genesis


@pytest.fixture(scope="function")
def buffered_genesis(client_genesis: dict) -> io.BufferedReader:
    """
    Create a buffered reader for the genesis block header of the current test
    fixture.
    """
    genesis_json = json.dumps(client_genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))


@pytest.fixture(scope="function")
def client_files(buffered_genesis: io.BufferedReader) -> Mapping[str, io.BufferedReader]:
    """
    Define the files that hive will start the client with.
    """
    files = {}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="function")
def environment(blockchain_fixture: BlockchainHiveFixture) -> dict:
    """
    Define the environment that hive will start the client with using the fork
    rules specific for the simulator.
    """
    assert (
        blockchain_fixture.fork in ruleset
    ), f"fork '{blockchain_fixture.fork}' missing in hive ruleset"
    return {
        "HIVE_CHAIN_ID": "1",
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        **{k: f"{v:d}" for k, v in ruleset[blockchain_fixture.fork].items()},
    }


@pytest.fixture(scope="function")
def client(
    hive_test: HiveTest,
    client_files: dict,
    environment: dict,
    client_type: ClientType,
) -> Generator[Client, None, None]:
    """
    Initialize the client with the appropriate files and environment variables.
    """
    client = hive_test.start_client(
        client_type=client_type, environment=environment, files=client_files
    )
    error_message = (
        f"Unable to connect to the client container ({client_type.name}) via Hive during test "
        "setup. Check the client or Hive server logs for more information."
    )
    assert client is not None, error_message
    yield client
    client.stop()
