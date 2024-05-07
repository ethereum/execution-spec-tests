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
from pathlib import Path
from typing import Any, Generator, List, Literal, Mapping, Optional, Union, cast

import pytest
import requests
import rich
from hive.client import Client, ClientType
from hive.testing import HiveTest
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from ethereum_test_tools.common.base_types import Bytes
from ethereum_test_tools.common.json import to_json
from ethereum_test_tools.spec.blockchain.types import Fixture, FixtureHeader
from ethereum_test_tools.spec.consume.types import TestCaseIndexFile, TestCaseStream
from ethereum_test_tools.spec.file.types import BlockchainFixtures
from pytest_plugins.consume.consume import JsonSource
from pytest_plugins.consume.hive_ruleset import ruleset

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
        data = {field: self.format_float(value, precision) for field, value in self.dict().items()}
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
def fixture(fixture_source: JsonSource, test_case: TestCase) -> Fixture:
    """
    The test fixture.
    """
    if fixture_source == "stdin":
        assert isinstance(test_case, TestCaseStream), "Expected a stream test case"
        assert isinstance(test_case.fixture, Fixture), "Expected a blockchain test fixture"
        fixture = test_case.fixture
    else:
        assert isinstance(test_case, TestCaseIndexFile), "Expected an index file test case"
        # TODO: Optimize, json files will be loaded multiple times;
        # cache fixtures as for statetest?
        fixtures = BlockchainFixtures.from_file(Path(fixture_source) / test_case.json_path)
        fixture = fixtures[test_case.id]
    return fixture


@pytest.fixture(scope="function")
def client_genesis(fixture: Fixture) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(fixture.genesis)  # NOTE: to_json() excludes None values
    alloc = to_json(fixture.pre)
    # NOTE: nethermind requires account keys to not be prefixed by '0x'
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
    files = {f"/blocks/{i:04d}.rlp": block_rlp for i, block_rlp in enumerate(buffered_blocks_rlp)}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture
def environment(fixture: Fixture) -> dict:
    """
    Define the environment that hive will start the client with using the fork
    rules specific for the simulator.
    """
    env = {
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_CHAIN_ID": "1",
    }
    assert fixture.fork in ruleset, f"fork '{fixture.fork}' missing in hive ruleset"
    for k, v in ruleset[fixture.fork].items():
        env[k] = f"{v:d}"
    if fixture.seal_engine == "NoProof":
        env["HIVE_SKIP_POW"] = "1"
    return env


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
    assert client is not None
    yield client
    t_start = time.perf_counter()
    client.stop()
    timing_data.stop_client = time.perf_counter() - t_start


BlockNumberType = Union[int, Literal["latest", "earliest", "pending"]]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def get_block(client: Client, block_number: BlockNumberType) -> dict:
    """
    Retrieve the i-th block from the client using the JSON-RPC API.
    Retries up to two times (three attempts total) in case of an error or a timeout,
    with exponential backoff.
    """
    if isinstance(block_number, int):
        block_number_string = hex(block_number)
    else:
        block_number_string = block_number
    url = f"http://{client.ip}:8545"
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_number_string, False],
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    result = response.json().get("result")

    if result is None or "error" in result:
        error_info: Any = "result is None; and therefore contains no error info"
        error_code = None
        if result is not None:
            error_info = result["error"]
            error_code = error_info["code"]
        raise Exception(
            f"Error calling JSON RPC eth_getBlockByNumber, code: {error_code}, "
            f"message: {error_info}"
        )

    return result


def compare_models(expected: BaseModel, got: BaseModel) -> dict:
    """
    Compare two pydantic model instances and return the differences.
    """
    differences = {}
    for field in expected.__fields__.keys():
        if getattr(expected, field) != getattr(got, field):
            differences[field] = {
                "expected     ": str(getattr(expected, field)),
                "got (via rpc)": str(getattr(got, field)),
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
    client: Client,
    fixture: Fixture,
    client_genesis: dict,
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
    genesis_block = get_block(client, 0)
    timing_data.get_genesis = time.perf_counter() - t_start
    if genesis_block["hash"] != str(fixture.genesis.block_hash):
        raise GenesisBlockMismatchException(
            expected_header=fixture.genesis, got_header=FixtureHeader(**genesis_block)
        )
    block = get_block(client, "latest")
    timing_data.get_last_block = time.perf_counter() - timing_data.get_genesis - t_start
    assert block["hash"] == str(fixture.last_block_hash), "hash mismatch in last block"
