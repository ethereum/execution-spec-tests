"""
A hive simulator that executes blocks against clients using the
`engine_newPayloadVX` method from the Engine API, verifying
the appropriate VALID/INVALID responses.

Implemented using the pytest framework as a pytest plugin.
"""
import io
import json
from typing import Dict, List, Mapping

import pytest
from hive.client import Client, ClientType
from hive.testing import HiveTest

# TODO: Replace with entire fork enum
from ethereum_test_forks import (  # noqa: F401
    Berlin,
    Cancun,
    Frontier,
    London,
    Merge,
    MergeToShanghaiAtTime15k,
    Shanghai,
    ShanghaiToCancunAtTime15k,
)
from ethereum_test_tools.common.json import load_dataclass_from_json
from ethereum_test_tools.common.types import Account, FixtureBlock, FixtureEngineNewPayload
from ethereum_test_tools.rpc import EngineRPC, EthRPC
from pytest_plugins.consume.consume import TestCase
from pytest_plugins.consume_via_engine_api.client_fork_ruleset import client_fork_ruleset


@pytest.fixture(scope="function")
def buffered_genesis(test_case: TestCase) -> Dict[str, io.BufferedReader]:
    """
    Convert the genesis block header of the current test fixture to a buffered reader
    readable by the client under test within hive.
    """
    # Extract genesis and pre-alloc from test case fixture
    genesis = test_case.fixture.genesis
    pre_alloc = test_case.json_as_dict["pre"]
    genesis["alloc"] = pre_alloc

    # Convert client genesis to BufferedReader
    genesis_json = json.dumps(genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(io.BytesIO(genesis_bytes))


@pytest.fixture(scope="function")
def client_files(
    client_type: ClientType, buffered_genesis: io.BufferedReader
) -> Mapping[str, io.BufferedReader]:
    """
    Defines the files that hive will start the client with.
    The buffered genesis including the pre-alloc.
    """
    files = {}
    # Client specific genesis format
    if client_type.name == "nethermind":
        files["/chainspec/test.json"] = buffered_genesis
    else:
        files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="function")
def client_environment(test_case: TestCase) -> Dict:
    """
    Defines the environment that hive will start the client with
    using the fork rules specific for the simulator.
    """
    client_env = {
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_CHAIN_ID": "1",
        "HIVE_NODETYPE": "full",
        **{k: f"{v:d}" for k, v in client_fork_ruleset.get(test_case.fixture.fork, {}).items()},
    }
    return client_env


@pytest.fixture(scope="function")
def client(
    hive_test: HiveTest, client_files: Dict, client_environment: Dict, client_type: ClientType
) -> Client:
    """
    Initializes the client with the appropriate files and environment variables.
    """
    client = hive_test.start_client(
        client_type=client_type, environment=client_environment, files=client_files
    )
    assert client is not None
    yield client
    client.stop()


@pytest.fixture(scope="function")
def engine_rpc(client: Client) -> EngineRPC:
    """
    Initializes the engine RPC for the client under test.
    """
    return EngineRPC(client)


@pytest.fixture(scope="function")
def eth_rpc(client: Client) -> EngineRPC:
    """
    Initializes the eth RPC for the client under test.
    """
    return EthRPC(client)


@pytest.fixture(scope="function")
def engine_new_payloads(test_case: TestCase) -> List[FixtureEngineNewPayload]:
    """
    Execution payloads extracted from each block within the test case fixture.
    Sent to the client under test using the `engine_newPayloadVX` method from the Engine API.
    """
    fixture_blocks = [
        load_dataclass_from_json(FixtureBlock, block.get("rlp_decoded", block))
        for block in test_case.fixture.blocks
    ]

    return [
        FixtureEngineNewPayload.from_fixture_header(
            globals()[test_case.fixture.fork],
            block.block_header,
            block.txs,
            block.withdrawals,
            False if block.expected_exception else True,
            error_code=None,
        )
        for block in fixture_blocks
    ]


def test_via_engine_api(
    test_case: TestCase,
    engine_new_payloads: List[FixtureEngineNewPayload],
    engine_rpc: EngineRPC,
    eth_rpc: EthRPC,
):
    """
    1) Checks that the genesis block hash of the client matches that of the fixture.
    2) Executes the test case fixture blocks against the client under test using the
    `engine_newPayloadVX` method from the Engine API, verifying the appropriate
    VALID/INVALID responses.
    3) Performs a forkchoice update to finalize the chain and verify the post state.
    4) Checks that the post state of the client matches that of the fixture.
    """
    genesis_block = eth_rpc.get_block_by_number(0, False)
    assert genesis_block["hash"] == test_case.fixture.genesis["hash"], "genesis hash mismatch"

    for payload in engine_new_payloads:
        payload_response = engine_rpc.new_payload(payload)
        assert payload_response["status"] == (
            "VALID" if payload.valid else "INVALID"
        ), f"unexpected status: {payload_response} "

    forkchoice_response = engine_rpc.forkchoice_updated(
        forkchoice_state={"headBlockHash": engine_new_payloads[-1].payload.hash},
        payload_attributes=None,
        version=engine_new_payloads[-1].version,
    )
    assert (
        forkchoice_response["payloadStatus"]["status"] == "VALID"
    ), f"forkchoice update failed: {forkchoice_response}"

    for address, account in test_case.fixture.post_state.items():
        verify_account_state_and_storage(eth_rpc, address.hex(), account, test_case.fixture_name)


def verify_account_state_and_storage(eth_rpc, address, account: Account, test_name):
    """
    Verify the account state and storage matches the expected account state and storage.
    """
    # Check final nonce matches expected in fixture
    nonce = eth_rpc.get_transaction_count(address)
    assert int(account.nonce, 16) == int(
        nonce, 16
    ), f"Nonce mismatch for account {address} in test {test_name}"

    # Check final balance
    balance = eth_rpc.get_balance(address)
    assert int(account.balance, 16) == int(
        balance, 16
    ), f"Balance mismatch for account {address} in test {test_name}"

    # Check final storage
    if len(account.storage) > 0:
        keys = list(account.storage.keys())
        storage = eth_rpc.storage_at_keys(address, keys)
        for key in keys:
            assert int(account.storage[key], 16) == int(
                storage[key], 16
            ), f"Storage mismatch for account {address}, key {key} in test {test_name}"
