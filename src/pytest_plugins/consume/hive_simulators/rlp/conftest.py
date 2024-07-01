"""
Pytest fixtures and classes for the `consume rlp` hive simulator.
"""

import io
import json
import time
from pathlib import Path
from typing import Generator, List, Mapping, Optional, cast

import pytest
import rich
from hive.client import Client, ClientType
from hive.testing import HiveTest
from pydantic import BaseModel

from ethereum_test_base_types import Bytes, to_json
from ethereum_test_fixtures import BlockchainFixture
from ethereum_test_fixtures.consume import TestCaseIndexFile, TestCaseStream
from ethereum_test_fixtures.file import BlockchainFixtures
from ethereum_test_tools.rpc import EthRPC
from pytest_plugins.consume.common import JsonSource
from pytest_plugins.consume.hive_simulators.ruleset import ruleset  # TODO: generate dynamically

TestCase = TestCaseIndexFile | TestCaseStream


class TestCaseTimingData(BaseModel):
    """
    The times taken to perform the various steps of a test case (seconds).
    """

    __test__ = False
    prepare_files: Optional[float] = None  # start of test until client start
    start_client: Optional[float] = None
    get_genesis: Optional[float] = None
    get_last_block: Optional[float] = None
    stop_client: Optional[float] = None
    total: Optional[float] = None

    @staticmethod
    def format_float(num: float | None, precision: int = 4) -> str | None:
        """
        Format a float to a specific precision in significant figures.
        """
        if num is None:
            return None
        return f"{num:.{precision}f}"

    def formatted(self, precision: int = 4) -> "TestCaseTimingData":
        """
        Return a new instance of the model with formatted float values.
        """
        data = {field: self.format_float(value, precision) for field, value in self}
        return TestCaseTimingData(**data)


@pytest.fixture(scope="session")
def test_suite_name() -> str:
    """
    The name of the hive test suite used in this simulator.
    """
    return "eest-rlp"


@pytest.fixture(scope="session")
def test_suite_description() -> str:
    """
    The description of the hive test suite used in this simulator.
    """
    return "Execute blockchain tests by providing RLP-encoded blocks to a client upon start-up."


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    return EthRPC(ip=client.ip)


@pytest.fixture(scope="function")
def blockchain_fixture(fixture_source: JsonSource, test_case: TestCase) -> BlockchainFixture:
    """
    Create the blockchain fixture pydantic model for the current test case.

    The fixture is either already available within the test case (if consume
    is taking input on stdin) or loaded from the fixture json file if taking
    input from disk (fixture directory with index file).
    """
    if fixture_source == "stdin":
        assert isinstance(test_case, TestCaseStream), "Expected a stream test case"
        assert isinstance(
            test_case.fixture, BlockchainFixture
        ), "Expected a blockchain test fixture"
        fixture = test_case.fixture
    else:
        assert isinstance(test_case, TestCaseIndexFile), "Expected an index file test case"
        # TODO: Optimize, json files will be loaded multiple times. This pytest fixture
        # is executed per test case, and a fixture json will contain multiple test cases.
        fixtures = BlockchainFixtures.from_file(Path(fixture_source) / test_case.json_path)
        fixture = fixtures[test_case.id]
    return fixture


@pytest.fixture(scope="function")
def fixture_description(
    blockchain_fixture: BlockchainFixture, test_case: TestCaseIndexFile | TestCaseStream
) -> str:
    """
    Create the description of the current blockchain fixture test case.
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
def t_test_start() -> float:
    """
    The time the test started; used to time fixture+file preparation and total time.
    """
    return time.perf_counter()


@pytest.fixture(scope="function", autouse=True)
def timing_data(request, t_test_start) -> Generator[TestCaseTimingData, None, None]:
    """
    Helper to record timing data for various stages of executing test case.
    """
    timing_data = TestCaseTimingData()
    yield timing_data
    timing_data.total = time.perf_counter() - t_test_start
    rich.print(f"\nTimings (seconds): {timing_data.formatted()}")
    if hasattr(request.node, "rep_call"):  # make available for test reports
        request.node.rep_call.timings = timing_data


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("timing_data")
def client_genesis(blockchain_fixture: BlockchainFixture) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(blockchain_fixture.genesis)  # NOTE: to_json() excludes None values
    alloc = to_json(blockchain_fixture.pre)
    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
    return genesis


@pytest.fixture(scope="function")
def blocks_rlp(blockchain_fixture: BlockchainFixture) -> List[Bytes]:
    """
    A list of the fixture's blocks encoded as RLP.
    """
    return [block.rlp for block in blockchain_fixture.blocks]


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
def buffered_blocks_rlp(blocks_rlp: List[bytes]) -> List[io.BufferedReader]:
    """
    Convert the RLP-encoded blocks of the current test fixture to buffered readers.
    """
    block_rlp_files = []
    for _, block_rlp in enumerate(blocks_rlp):
        block_rlp_stream = io.BytesIO(block_rlp)
        block_rlp_files.append(io.BufferedReader(cast(io.RawIOBase, block_rlp_stream)))
    return block_rlp_files


@pytest.fixture(scope="function")
def client_files(
    buffered_genesis: io.BufferedReader,
    buffered_blocks_rlp: list[io.BufferedReader],
) -> Mapping[str, io.BufferedReader]:
    """
    Define the files that hive will start the client with.

    The files are specified as a dictionary whose:
    - Keys are the target file paths in the client's docker container, and,
    - Values are in-memory buffered file objects.
    """
    files = {f"/blocks/{i + 1:04d}.rlp": rlp for i, rlp in enumerate(buffered_blocks_rlp)}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="function")
def environment(blockchain_fixture: BlockchainFixture) -> dict:
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
