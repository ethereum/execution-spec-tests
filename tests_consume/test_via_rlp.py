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
from pathlib import Path
from typing import List, Literal, Mapping, Union

import pytest
import requests
from hive.client import Client, ClientType
from hive.testing import HiveTest
from tenacity import retry, stop_after_attempt, wait_exponential

from ethereum_test_tools.common.base_types import Bytes, Hash
from ethereum_test_tools.common.json import to_json
from ethereum_test_tools.spec.blockchain.types import Fixture, FixtureBlock
from ethereum_test_tools.spec.consume.types import TestCaseIndexFile, TestCaseStream
from ethereum_test_tools.spec.file.types import BlockchainFixtures
from pytest_plugins.consume.consume import JsonSource
from pytest_plugins.consume_via_rlp.network_ruleset_hive import ruleset

TestCase = TestCaseIndexFile | TestCaseStream


@pytest.fixture(scope="function")
def fixture(fixture_source: JsonSource, test_case: TestCase) -> Fixture:
    """
    The test fixture.
    """
    if fixture_source == "stdin":
        assert isinstance(test_case, TestCaseStream), "Expected a stream test case"
        assert isinstance(test_case.fixture, Fixture), "Expected a blockchain test fixture"
        fixture = test_case.fixture
    assert isinstance(test_case, TestCaseIndexFile), "Expected an index file test case"
    # TODO: Optimize - json files will be loaded multiple times; cache fixtures as for statetest?
    fixtures = BlockchainFixtures.from_file(Path(fixture_source) / test_case.json_path)
    fixture = fixtures[test_case.id]
    if any(
        block in fixture.blocks for block in fixture.blocks if not isinstance(block, FixtureBlock)
    ):
        pytest.skip("Expected all blocks to be of type FixtureBlock")
    return fixture


@pytest.fixture(scope="function")
def expected_hash(fixture: Fixture) -> Hash:
    """
    The fixture's last block header hash.
    """
    last_block = fixture.blocks[-1]
    assert isinstance(last_block, FixtureBlock), "Expected a valid block fixture"
    return last_block.header.block_hash


@pytest.fixture(scope="function")
def expected_state_root(fixture: Fixture) -> Hash:
    """
    The fixture's last block header state root.
    """
    last_block = fixture.blocks[-1]
    assert isinstance(last_block, FixtureBlock), "Expected a valid block fixture"
    return last_block.header.state_root


@pytest.fixture(scope="function")
def blocks_rlp(fixture: Fixture) -> List[Bytes]:
    """
    A list of the fixture's RLP-encoded blocks.
    """
    return [block.rlp for block in fixture.blocks]


@pytest.fixture(scope="function")
def to_geth_genesis(fixture: Fixture) -> dict:
    """
    Convert the genesis block header of the current test fixture to a geth genesis block.
    """
    genesis_json_data = to_json(fixture.genesis)  # None values are excluded
    geth_genesis = {
        k: v
        for k, v in genesis_json_data.items()
        if k
        in [
            "nonce",
            "timestamp",
            "extraData",
            "gasLimit",
            "difficulty",
            "mixhash",
            "coinbase",
            "baseFeePerGas",
            "withdrawalsRoot",
            "blobFeePerGas",
            "blobGasUsed",
        ]
    }
    geth_genesis["alloc"] = to_json(fixture.pre)
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
        blocks_rlp_bytes = block_rlp  # bytes.fromhex(block_rlp[2:])
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
def environment(fixture: Fixture) -> dict:
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
    fixture: Fixture,
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
    assert genesis_block["hash"] == fixture.genesis.block_hash, "genesis hash mismatch"

    block = get_block(client, "latest")
    assert block["number"] == hex(len(fixture.blocks)), "unexpected latest block number"
    # print("\n     got state root", block["stateRoot"], "hash", block["hash"])
    # print("expected state root", expected_state_root, "hash", expected_hash)
    assert block["stateRoot"] == expected_state_root, "state root mismatch in last block"
    assert block["hash"] == expected_hash, "hash mismatch in last block"
