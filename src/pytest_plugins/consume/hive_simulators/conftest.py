"""
Common pytest fixtures for the RLP and Engine simulators.
"""
import io
import json
import time
from typing import Generator, List, Mapping, cast

import pytest
import rich
from hive.client import Client, ClientType
from hive.testing import HiveTest
from pydantic import BaseModel

from ethereum_test_base_types import Bytes, to_json
from ethereum_test_fixtures import BlockchainFixtureCommon
from ethereum_test_fixtures.consume import TestCaseIndexFile, TestCaseStream
from ethereum_test_tools.rpc import EthRPC
from pytest_plugins.consume.hive_simulators.ruleset import ruleset  # TODO: generate dynamically


class TestCaseTimingData(BaseModel):
    """
    The times taken to perform the various steps of a test case (seconds).
    """

    __test__ = False
    prepare_files: float | None = None  # start of test until client start
    start_client: float | None = None
    get_genesis: float | None = None
    get_last_block: float | None = None
    stop_client: float | None = None
    total: float | None = None

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


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    return EthRPC(ip=client.ip)


@pytest.fixture(scope="function")
def fixture_description(
    blockchain_fixture: BlockchainFixtureCommon, test_case: TestCaseIndexFile | TestCaseStream
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
def client_genesis(blockchain_fixture: BlockchainFixtureCommon) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(blockchain_fixture.genesis)  # NOTE: to_json() excludes None values
    alloc = to_json(blockchain_fixture.pre)
    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
    return genesis


@pytest.fixture(scope="function")
def environment(blockchain_fixture: BlockchainFixtureCommon) -> dict:
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
def blocks_rlp() -> List[Bytes]:
    """
    A list of the fixture's blocks encoded as RLP.

    By default, no blocks are placed into this fixture, but `rlp` consumer will override this.
    """
    return []


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
