"""
Test a fully instantiated client using RLP-encoded blocks from blockchain tests.

The test fixtures should have the blockchain test format. The setup sends
the genesis file and RLP-encoded blocks to the client container using hive.
The client consumes these files upon start-up.

Given a genesis state and a list of RLP-encoded blocks, the test verifies that:
1. The client's genesis block hash matches that defined in the fixture.
2. The client's last block hash matches that defined in the fixture.
"""

import io
import json
import pprint
import time
from typing import Generator, List, Mapping, Optional, cast

import pytest
import rich
from hive.client import Client, ClientType
from hive.testing import HiveTest
from pydantic import BaseModel

from ethereum_test_tools.common.base_types import Bytes
from ethereum_test_tools.common.json import to_json
from ethereum_test_tools.rpc import EthRPC
from ethereum_test_tools.spec.blockchain.types import Fixture, FixtureHeader
from pytest_plugins.consume.hive_ruleset import ruleset


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
def client_genesis(fixture: Fixture) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(fixture.genesis)  # NOTE: to_json() excludes None values
    alloc = to_json(fixture.pre)
    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
    return genesis


@pytest.fixture(scope="function")
def blocks_rlp(fixture: Fixture) -> List[Bytes]:
    """
    A list of the fixture's blocks encoded as RLP.
    """
    return [block.rlp for block in fixture.blocks]


@pytest.fixture
def buffered_genesis(client_genesis: dict) -> io.BufferedReader:
    """
    Create a buffered reader for the genesis block header of the current test
    fixture.
    """
    genesis_json = json.dumps(client_genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))


@pytest.fixture
def buffered_blocks_rlp(blocks_rlp: List[bytes], start=1) -> List[io.BufferedReader]:
    """
    Convert the RLP-encoded blocks of the current test fixture to buffered readers.
    """
    block_rlp_files = []
    for i, block_rlp in enumerate(blocks_rlp):
        block_rlp_stream = io.BytesIO(block_rlp)
        block_rlp_files.append(io.BufferedReader(cast(io.RawIOBase, block_rlp_stream)))
    return block_rlp_files


@pytest.fixture
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


@pytest.fixture
def environment(fixture: Fixture) -> dict:
    """
    Define the environment that hive will start the client with using the fork
    rules specific for the simulator.
    """
    assert fixture.fork in ruleset, f"fork '{fixture.fork}' missing in hive ruleset"
    return {
        "HIVE_CHAIN_ID": "1",
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        **{k: f"{v:d}" for k, v in ruleset[fixture.fork].items()},
    }


@pytest.fixture(scope="function")
def client(
    hive_test: HiveTest,
    client_files: dict,
    environment: dict,
    client_type: ClientType,
    t_test_start: float,
    timing_data: TestCaseTimingData,
) -> Generator[Client, None, None]:
    """
    Initialize the client with the appropriate files and environment variables.
    """
    timing_data.prepare_files = time.perf_counter() - t_test_start
    t_start = time.perf_counter()
    client = hive_test.start_client(
        client_type=client_type, environment=environment, files=client_files
    )
    timing_data.start_client = time.perf_counter() - t_start
    error_message = (
        f"Unable to connect to the client container ({client_type.name}) via Hive during test "
        "setup. Check the client or Hive server logs for more information."
    )
    assert client is not None, error_message
    yield client
    t_start = time.perf_counter()
    client.stop()
    timing_data.stop_client = time.perf_counter() - t_start


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    return EthRPC(client_ip=client.ip)


def compare_models(expected: FixtureHeader, got: FixtureHeader) -> dict:
    """
    Compare two FixtureHeader model instances and return their differences.
    """
    differences = {}
    for (exp_name, exp_value), (_, got_value) in zip(expected, got):
        if exp_value != got_value:
            differences[exp_name] = {
                "expected     ": str(exp_value),
                "got (via rpc)": str(got_value),
            }
    return differences


class GenesisBlockMismatchException(Exception):
    """
    Used when the client's genesis block hash does not match the fixture.
    """

    def __init__(self, *, expected_header: FixtureHeader, got_header: FixtureHeader):
        message = (
            "Genesis block hash mismatch.\n"
            f"Expected: {expected_header.block_hash}\n"
            f"     Got: {got_header.block_hash}."
        )
        differences = compare_models(expected_header, got_header)
        if differences:
            message += (
                "\n\nAdditionally, there are differences between the expected and received "
                "genesis block header fields:\n"
                f"{pprint.pformat(differences, indent=4)}"
            )
        else:
            message += (
                "There were no differences in the expected and received genesis block headers."
            )
        super().__init__(message)


def test_via_rlp(
    eth_rpc: EthRPC,
    fixture: Fixture,
    timing_data: TestCaseTimingData,
):
    """
    Verify that the client's state as calculated from the specified genesis state
    and blocks matches those defined in the test fixture.

    Test:

    1. The client's genesis block hash matches `fixture.genesis.block_hash`.
    2. The client's last block's hash matches `fixture.last_block_hash`.
    """
    t_start = time.perf_counter()
    genesis_block = eth_rpc.get_block_by_number(0)
    timing_data.get_genesis = time.perf_counter() - t_start
    if genesis_block["hash"] != str(fixture.genesis.block_hash):
        raise GenesisBlockMismatchException(
            expected_header=fixture.genesis, got_header=FixtureHeader(**genesis_block)
        )
    block = eth_rpc.get_block_by_number("latest")
    timing_data.get_last_block = time.perf_counter() - timing_data.get_genesis - t_start
    assert block["hash"] == str(fixture.last_block_hash), "hash mismatch in last block"
