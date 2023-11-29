"""
Test module that defines a test to execute a fixture against an EVM blocktest-like command.
"""
import json
import tempfile
from pathlib import Path
from typing import List, Literal, Union

import pytest
import requests
from hive.client import Client
from hive.testing import HiveTest
from tenacity import retry, stop_after_attempt, wait_exponential

from ethereum_test_tools.common.types import Fixture
from pytest_plugins.consume_via_rlp.consume_via_rlp import TestCase
from pytest_plugins.consume_via_rlp.network_ruleset_hive import ruleset


@pytest.fixture(scope="function")
def temp_dir() -> tempfile.TemporaryDirectory:
    """
    Return a temporary directory to write the genesis.json and block RLP files to.
    """
    return tempfile.TemporaryDirectory()


@pytest.fixture(scope="function")
def test_case_fixture(test_case: TestCase) -> Fixture:
    """
    The test fixture as a dictionary.
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


@pytest.fixture(scope="session")
def network(test_suite):
    return test_suite.create_network("execution_client_network")


@pytest.fixture(scope="function")
def blocks_rlp(test_case_fixture: Fixture) -> List[str]:
    """
    A list of RLP-encoded blocks for the current test fixture.
    """
    return [block["rlp"] for block in test_case_fixture.blocks]


@pytest.fixture(scope="function")
def to_geth_genesis(test_case: TestCase, test_case_fixture: Fixture):
    """
    Convert the genesis block header of the current test fixture to a geth genesis block.
    """
    # TODO: Ask Martin why we can't just use the genesis block header as-is.
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
def genesis_file(to_geth_genesis: dict, temp_dir: tempfile.TemporaryDirectory) -> Path:
    genesis_file = Path(temp_dir.name) / "genesis.json"
    with open(genesis_file, "w") as f:
        f.write(json.dumps(to_geth_genesis))
    return genesis_file


@pytest.fixture
def block_rlp_files(temp_dir, blocks_rlp, start=1) -> List[Path]:
    block_rlp_files = []
    for i, block_rlp in enumerate(blocks_rlp):
        blocks_rlp_file = Path(temp_dir.name) / f"{i:04d}.rlp"
        with open(blocks_rlp_file, "wb") as f:
            f.write(bytes.fromhex(block_rlp[2:]))
        block_rlp_files.append(blocks_rlp_file)
    yield block_rlp_files


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


@pytest.fixture
def files(test_case: TestCase, genesis_file: Path, block_rlp_files: list[Path]):
    """
    Define the files that will be sent to the client container upon initializing
    the client.

    The files are specified as a dictionary whose:
    - Keys are the target file paths in the client's docker container, and,
    - Values are the source file paths in the simulator container, respectively
        the host (if hive is running in --dev mode).
    """
    target_block_files = [Path(f"/blocks/{file.name}") for file in block_rlp_files]
    target_genesis_file = Path("/genesis.json")
    files = {
        str(target_file): str(source_file)
        for target_file, source_file in zip(target_block_files, block_rlp_files)
    }
    files[str(target_genesis_file)] = str(genesis_file)
    return files


@pytest.fixture(scope="function")
def client(hive_test: HiveTest, files: dict, environment: dict, network, client_type) -> Client:
    client = hive_test.start_client(client_type=client_type, environment=environment, files=files)
    assert client is not None
    network.connect_client(client)
    yield client
    network.disconnect_client(client)
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
