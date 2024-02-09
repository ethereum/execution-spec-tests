"""
Test module to test clients using RLP-encoded blocks from blockchain tests.

The test fixtures should have the blockchain test format. The setup sends
the genesis file and RLP-encoded blocks to the client container using hive.
The client consumes these files upon start-up.

The test verifies:
1. The client's genesis block hash matches that of the fixture.
2. The client's last block's hash and stateRoot` match those of the fixture.
"""
import io
import json
from typing import List, Literal, Mapping, Union

import pytest
import requests
from hive.client import Client, ClientType
from hive.testing import HiveTest
from tenacity import retry, stop_after_attempt, wait_exponential

from ethereum_test_tools.spec.blockchain.types import Fixture
from pytest_plugins.consume.consume import TestCase
from pytest_plugins.consume_via_rlp.network_ruleset_hive import ruleset


@pytest.fixture(scope="function")
def test_case_fixture(test_case: TestCase) -> Fixture:
    """
    The test fixture as a dictionary.

    If we failed to parse a test case fixture, it's None: We xfail/skip the test.
    """
    assert test_case.fixture is not None
    return test_case.fixture


@pytest.fixture(scope="function")
def expected_hash(test_case_fixture: Fixture) -> str:
    """
    The hash defined in the test fixture's last block header.
    """
    return test_case_fixture.blocks[-1]["blockHeader"]["hash"]


@pytest.fixture(scope="function")
def expected_state_root(test_case: TestCase) -> str:
    """
    The state root defined in the test fixture's last block header.
    """
    return test_case.fixture.blocks[-1]["blockHeader"]["stateRoot"]


@pytest.fixture(scope="function")
def blocks_rlp(test_case_fixture: Fixture) -> List[str]:
    """
    A list of RLP-encoded blocks for the current json test fixture.
    """
    return [block["rlp"] for block in test_case_fixture.blocks]


@pytest.fixture(scope="function")
def to_geth_genesis(test_case: TestCase, test_case_fixture: Fixture) -> dict:
    """
    Convert the genesis block header of the current test fixture to a geth genesis block.
    """
    geth_genesis = {
        "nonce": test_case_fixture.genesis["nonce"],
        "timestamp": test_case_fixture.genesis["timestamp"],
        "extraData": test_case_fixture.genesis["extraData"],
        "gasLimit": test_case_fixture.genesis["gasLimit"],
        "difficulty": test_case_fixture.genesis["difficulty"],
        "mixhash": test_case_fixture.genesis["mixHash"],
        "coinbase": test_case_fixture.genesis["coinbase"],
        # TODO: retrieve pre_state from the fixture? Instead of the json
        # (and potentially remove the json_as_dict field completely from TestCase)
        "alloc": test_case.json_as_dict["pre"],
    }
    # TODO: Use ethereum_test_forks to detect new fields automatically?
    for field in ["baseFeePerGas", "withdrawalsRoot", "blobFeePerGas", "blobGasUsed"]:
        if field in test_case_fixture.genesis:
            geth_genesis[field] = test_case_fixture.genesis[field]
    return geth_genesis


@pytest.fixture
def buffered_genesis(to_geth_genesis: dict) -> io.BufferedReader:
    genesis_json = json.dumps(to_geth_genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(io.BytesIO(genesis_bytes))


@pytest.fixture
def buffered_blocks_rlp(blocks_rlp: List[str], start=1) -> List[io.BufferedReader]:
    block_rlp_files = []
    for i, block_rlp in enumerate(blocks_rlp):
        blocks_rlp_bytes = bytes.fromhex(block_rlp[2:])
        blocks_rlp_stream = io.BytesIO(blocks_rlp_bytes)
        block_rlp_files.append(io.BufferedReader(blocks_rlp_stream))
    return block_rlp_files


@pytest.fixture
def files(
    test_case: TestCase,
    client_type: ClientType,
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
    if client_type.name == "nethermind":
        files["/chainspec/test.json"] = buffered_genesis
    else:
        files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture
def environment(test_case: TestCase) -> dict:
    env = {
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_CHAIN_ID": "1",
    }
    assert test_case.fixture.fork in ruleset, "Oops, should never get here"
    for k, v in ruleset[test_case.fixture.fork].items():
        env[k] = f"{v:d}"
    if test_case.fixture.seal_engine == "NoProof":
        env["HIVE_SKIP_POW"] = "1"
    return env


@pytest.fixture(scope="function")
def client(hive_test: HiveTest, files: dict, environment: dict, client_type: ClientType) -> Client:
    client = hive_test.start_client(client_type=client_type, environment=environment, files=files)
    assert client is not None
    yield client
    client.stop()


BlockNumberType = Union[int, Literal["latest", "earliest", "pending"]]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
def get_block(client: Client, block_number: BlockNumberType) -> dict:
    """
    Retrieve the i-th block from the client using the JSON-RPC API.
    Retries up to two times (three attempts total) in case of an error or a timeout,
    with exponential backoff.
    """
    if isinstance(block_number, int):
        block_number = hex(block_number)
    url = f"http://{client.ip}:8545"
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_number, False],
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    result = response.json().get("result")

    if result is None or "error" in result:
        error_info = "result is None; and therefore contains no error info"
        error_code = None
        if result is not None:
            error_info = result["error"]
            error_code = error_info["code"]
        raise Exception(
            f"Error calling JSON RPC eth_getBlockByNumber, code: {error_code}, "
            f"message: {error_info}"
        )

    return result


def test_via_rlp(
    client: Client,
    test_case: TestCase,
    expected_hash: str,
    expected_state_root: str,
):
    """
    Verify that the client's state as calculated from the specified genesis state
    and blocks matches those defined in the test fixture.

    Test:

    1. The client's genesis block hash matches that of the fixture.
    2. The client's last block's hash and stateRoot` match those of the fixture.
    """
    genesis_block = get_block(client, 0)
    assert genesis_block["hash"] == test_case.fixture.genesis["hash"], "genesis hash mismatch"

    block = get_block(client, "latest")
    assert block["number"] == hex(len(test_case.fixture.blocks)), "unexpected latest block number"
    # print("\n     got state root", block["stateRoot"], "hash", block["hash"])
    # print("expected state root", expected_state_root, "hash", expected_hash)
    assert block["stateRoot"] == expected_state_root, "state root mismatch in last block"
    assert block["hash"] == expected_hash, "hash mismatch in last block"
