"""
Pytest plugin to run the test-execute in hive-mode.
"""

import io
import json
import time
from threading import Lock
from typing import Any, Generator, Iterator, List, Mapping, Tuple, cast

import pytest
from ethereum.crypto.hash import keccak256
from hive.client import Client, ClientType
from hive.simulation import Simulation
from hive.testing import HiveTest, HiveTestResult, HiveTestSuite

from ethereum_test_base_types import EmptyOmmersRoot, EmptyTrieRoot, to_json
from ethereum_test_fixtures.blockchain import FixtureHeader
from ethereum_test_forks import Fork, get_forks
from ethereum_test_rpc import EngineRPC
from ethereum_test_rpc import EthRPC as BaseEthRPC
from ethereum_test_rpc.types import (
    ForkchoiceState,
    PayloadAttributes,
    PayloadStatusEnum,
    TransactionByHashResponse,
)
from ethereum_test_tools import (
    EOA,
    Account,
    Address,
    Alloc,
    Environment,
    Hash,
    Transaction,
    Withdrawal,
)
from ethereum_test_types import Requests
from pytest_plugins.consume.hive_simulators.ruleset import ruleset


def get_fork_option(request, option_name: str) -> Fork | None:
    """Post-process get option to allow for external fork conditions."""
    option = request.config.getoption(option_name)
    if option := request.config.getoption(option_name):
        if option == "Merge":
            option = "Paris"
        for fork in get_forks():
            if option == fork.name():
                return fork
    return None


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    hive_rpc_group = parser.getgroup(
        "senders", "Arguments defining sender keys used to fund tests."
    )
    hive_rpc_group.addoption(
        "--transactions-per-block",
        action="store",
        dest="transactions_per_block",
        type=int,
        default=1,
        help=("Number of transactions to send before producing the next block."),
    )


def pytest_configure(config):  # noqa: D103
    config.test_suite_scope = "session"


@pytest.fixture(scope="session")
def base_fork(request) -> Fork:
    """
    Get the base fork for all tests.
    """
    fork = get_fork_option(request, "single_fork")
    assert fork is not None, "invalid fork requested"
    return fork


@pytest.fixture(scope="session")
def seed_sender(request, eoa_iterator: Iterator[EOA]) -> EOA:
    """
    Setup the seed sender account by checking its balance and nonce.
    """
    return next(eoa_iterator)


@pytest.fixture(scope="session")
def base_pre(request, seed_sender: EOA) -> Alloc:
    """
    Base pre-allocation for the client's genesis.
    """
    sender_key_count = request.config.getoption("sender_key_count")
    sender_key_initial_balance = request.config.getoption("sender_key_initial_balance")
    return Alloc(
        {seed_sender: Account(balance=sender_key_count * sender_key_initial_balance + 10**18)}
    )


@pytest.fixture(scope="session")
def base_pre_genesis(
    base_fork: Fork,
    base_pre: Alloc,
) -> Tuple[Alloc, FixtureHeader]:
    """
    Create a genesis block from the blockchain test definition.
    """
    env = Environment().set_fork_requirements(base_fork)
    assert (
        env.withdrawals is None or len(env.withdrawals) == 0
    ), "withdrawals must be empty at genesis"
    assert env.parent_beacon_block_root is None or env.parent_beacon_block_root == Hash(
        0
    ), "parent_beacon_block_root must be empty at genesis"

    pre_alloc = Alloc.merge(
        Alloc.model_validate(base_fork.pre_allocation_blockchain()),
        base_pre,
    )
    if empty_accounts := pre_alloc.empty_accounts():
        raise Exception(f"Empty accounts in pre state: {empty_accounts}")
    state_root = pre_alloc.state_root()
    genesis = FixtureHeader(
        parent_hash=0,
        ommers_hash=EmptyOmmersRoot,
        fee_recipient=0,
        state_root=state_root,
        transactions_trie=EmptyTrieRoot,
        receipts_root=EmptyTrieRoot,
        logs_bloom=0,
        difficulty=0x20000 if env.difficulty is None else env.difficulty,
        number=0,
        gas_limit=env.gas_limit,
        gas_used=0,
        timestamp=1,
        extra_data=b"\x00",
        prev_randao=0,
        nonce=0,
        base_fee_per_gas=env.base_fee_per_gas,
        blob_gas_used=env.blob_gas_used,
        excess_blob_gas=env.excess_blob_gas,
        withdrawals_root=Withdrawal.list_root(env.withdrawals)
        if env.withdrawals is not None
        else None,
        parent_beacon_block_root=env.parent_beacon_block_root,
        requests_root=Requests(root=[]).trie_root
        if base_fork.header_requests_required(0, 0)
        else None,
    )

    return (pre_alloc, genesis)


@pytest.fixture(scope="session")
def base_genesis_header(base_pre_genesis: Tuple[Alloc, FixtureHeader]) -> FixtureHeader:
    """
    Return the genesis header for the current test fixture.
    """
    return base_pre_genesis[1]


@pytest.fixture(scope="session")
def client_genesis(base_pre_genesis: Tuple[Alloc, FixtureHeader]) -> dict:
    """
    Convert the fixture's genesis block header and pre-state to a client genesis state.
    """
    genesis = to_json(base_pre_genesis[1])  # NOTE: to_json() excludes None values
    alloc = to_json(base_pre_genesis[0])
    # NOTE: nethermind requires account keys without '0x' prefix
    genesis["alloc"] = {k.replace("0x", ""): v for k, v in alloc.items()}
    return genesis


@pytest.fixture(scope="session")
def buffered_genesis(client_genesis: dict) -> io.BufferedReader:
    """
    Create a buffered reader for the genesis block header of the current test
    fixture.
    """
    genesis_json = json.dumps(client_genesis)
    genesis_bytes = genesis_json.encode("utf-8")
    return io.BufferedReader(cast(io.RawIOBase, io.BytesIO(genesis_bytes)))


@pytest.fixture(scope="session")
def client_files(
    buffered_genesis: io.BufferedReader,
) -> Mapping[str, io.BufferedReader]:
    """
    Define the files that hive will start the client with.

    For this type of test, only the genesis is passed
    """
    files = {}
    files["/genesis.json"] = buffered_genesis
    return files


@pytest.fixture(scope="session")
def environment(base_fork: Fork) -> dict:
    """
    Define the environment that hive will start the client with using the fork
    rules specific for the simulator.
    """
    assert base_fork.name() in ruleset, f"fork '{base_fork.name()}' missing in hive ruleset"
    return {
        "HIVE_CHAIN_ID": "1",
        "HIVE_FORK_DAO_VOTE": "1",
        "HIVE_NODETYPE": "full",
        **{k: f"{v:d}" for k, v in ruleset[base_fork.name()].items()},
    }


@pytest.fixture(scope="session")
def test_suite_name() -> str:
    """
    The name of the hive test suite used in this simulator.
    """
    return "EEST Execute Test, Hive Mode"


@pytest.fixture(scope="session")
def test_suite_description() -> str:
    """
    The description of the hive test suite used in this simulator.
    """
    return "Execute EEST tests using hive endpoint."


@pytest.fixture(autouse=True, scope="session")
def base_hive_test(test_suite: HiveTestSuite):
    """
    Base test used to deploy the main client to be used throughout all tests.
    """
    test: HiveTest = test_suite.start_test(
        name="base_test",
        description="Base test to deploy the main client to be used throughout all tests.",
    )
    yield test
    test.end(result=HiveTestResult(test_pass=True, details="All tests have completed"))


@pytest.fixture(autouse=True, scope="function")
def hive_test(request, test_suite: HiveTestSuite):
    """
    Base test used to deploy the main client to be used throughout all tests.
    """
    test: HiveTest = test_suite.start_test(
        name=request.node.nodeid,
        description=request.node.function.__doc__,
    )
    yield test
    try:
        # TODO: Handle xfail/skip, does this work with run=False?
        if hasattr(request.node, "result_call") and request.node.result_call.passed:
            test_passed = True
            test_result_details = "Test passed."
        elif hasattr(request.node, "result_call") and not request.node.result_call.passed:
            test_passed = False
            test_result_details = request.node.result_call.longreprtext
        elif hasattr(request.node, "result_setup") and not request.node.result_setup.passed:
            test_passed = False
            test_result_details = "Test setup failed.\n" + request.node.result_setup.longreprtext
        elif hasattr(request.node, "result_teardown") and not request.node.result_teardown.passed:
            test_passed = False
            test_result_details = (
                "Test teardown failed.\n" + request.node.result_teardown.longreprtext
            )
        else:
            test_passed = False
            test_result_details = "Test failed for unknown reason (setup or call status unknown)."
    except Exception as e:
        test_passed = False
        test_result_details = f"Exception whilst processing test result: {str(e)}"
    test.end(result=HiveTestResult(test_pass=test_passed, details=test_result_details))


@pytest.fixture(scope="session")
def client_type(simulator: Simulation) -> ClientType:
    """
    The type of client to be used in the test.
    """
    return simulator.client_types()[0]


@pytest.fixture(autouse=True, scope="session")
def client(
    base_hive_test: HiveTest,
    client_files: dict,
    environment: dict,
    client_type: ClientType,
) -> Generator[Client, None, None]:
    """
    Initialize the client with the appropriate files and environment variables.
    """
    client = base_hive_test.start_client(
        client_type=client_type, environment=environment, files=client_files
    )
    error_message = (
        f"Unable to connect to the client container ({client_type.name}) via Hive during test "
        "setup. Check the client or Hive server logs for more information."
    )
    assert client is not None, error_message
    yield client
    client.stop()


class EthRPC(BaseEthRPC):
    """
    Ethereum RPC client for the hive simulator which automatically sends Engine API requests to
    generate blocks after a certain number of transactions have been sent.
    """

    fork: Fork
    engine_rpc: EngineRPC
    transactions_per_block: int
    pending_tx_hashes: List[Hash] = []
    included_tx_hashes: List[Hash] = []
    parent_timestamp: int = 0
    parent_hash: Hash = Hash(0)
    get_payload_wait_time: int = 1
    _pending_hashes_lock: Lock = Lock()

    def __init__(
        self,
        *,
        client: Client,
        fork: Fork,
        genesis_header: FixtureHeader,
        transactions_per_block: int = 1,
    ):
        """
        Initialize the Ethereum RPC client for the hive simulator.
        """
        super().__init__(f"http://{client.ip}:8545")
        self.fork = fork
        self.engine_rpc = EngineRPC(f"http://{client.ip}:8551")
        self.parent_timestamp = genesis_header.timestamp
        self.parent_hash = genesis_header.block_hash
        self.transactions_per_block = transactions_per_block

        # Send initial forkchoice updated
        forkchoice_state = ForkchoiceState(
            head_block_hash=self.parent_hash,
        )
        forkchoice_version = self.fork.engine_forkchoice_updated_version()
        assert forkchoice_version is not None, "Fork does not support engine forkchoice_updated"
        response = self.engine_rpc.forkchoice_updated(
            forkchoice_state,
            None,
            version=forkchoice_version,
        )
        assert (
            response.payload_status.status == PayloadStatusEnum.VALID
        ), "Initial forkchoice_updated was invalid"

    def generate_block(self: "EthRPC"):
        """
        Generate a block using the Engine API.
        """
        forkchoice_state = ForkchoiceState(
            head_block_hash=self.parent_hash,
        )
        parent_beacon_block_root = Hash(0) if self.fork.header_beacon_root_required(0, 0) else None
        payload_attributes = PayloadAttributes(
            timestamp=self.parent_timestamp + 1,
            prev_randao=Hash(0),
            suggested_fee_recipient=Address(0),
            withdrawals=[] if self.fork.header_withdrawals_required() else None,
            parent_beacon_block_root=parent_beacon_block_root,
        )
        forkchoice_updated_version = self.fork.engine_forkchoice_updated_version()
        assert (
            forkchoice_updated_version is not None
        ), "Fork does not support engine forkchoice_updated"
        response = self.engine_rpc.forkchoice_updated(
            forkchoice_state,
            payload_attributes,
            version=forkchoice_updated_version,
        )
        assert response.payload_status.status == PayloadStatusEnum.VALID, "Payload was invalid"
        assert response.payload_id is not None, "payload_id was not returned by the client"
        time.sleep(self.get_payload_wait_time)
        get_payload_version = self.fork.engine_get_payload_version()
        assert get_payload_version is not None, "Fork does not support engine get_payload"
        new_payload = self.engine_rpc.get_payload(
            response.payload_id,
            version=get_payload_version,
        )
        new_payload_args: List[Any] = [new_payload.execution_payload]
        if new_payload.blobs_bundle is not None:
            new_payload_args.append(new_payload.blobs_bundle.blob_versioned_hashes())
        if parent_beacon_block_root is not None:
            new_payload_args.append(parent_beacon_block_root)
        new_payload_version = self.fork.engine_new_payload_version()
        assert new_payload_version is not None, "Fork does not support engine new_payload"
        new_payload_response = self.engine_rpc.new_payload(
            *new_payload_args, version=new_payload_version
        )
        assert new_payload_response.status == PayloadStatusEnum.VALID, "Payload was invalid"

        new_forkchoice_state = ForkchoiceState(
            head_block_hash=new_payload.execution_payload.block_hash,
        )
        response = self.engine_rpc.forkchoice_updated(
            new_forkchoice_state,
            None,
            version=forkchoice_updated_version,
        )
        assert response.payload_status.status == PayloadStatusEnum.VALID, "Payload was invalid"
        for tx in new_payload.execution_payload.transactions:
            tx_hash = Hash(keccak256(tx))
            self.included_tx_hashes.append(tx_hash)
            if tx_hash in self.pending_tx_hashes:
                self.pending_tx_hashes.remove(tx_hash)
        self.parent_timestamp = new_payload.execution_payload.timestamp
        self.parent_hash = new_payload.execution_payload.block_hash

    def send_transaction(self, transaction: Transaction):
        """
        `eth_sendRawTransaction`: Send a transaction to the client.
        """
        super().send_transaction(transaction)
        with self._pending_hashes_lock:
            self.pending_tx_hashes.append(transaction.hash)
            if len(self.pending_tx_hashes) >= self.transactions_per_block:
                self.generate_block()

    def wait_for_transaction(
        self, transaction: Transaction, timeout: int = 60
    ) -> TransactionByHashResponse:
        """
        Uses `eth_getTransactionByHash` to wait until a transaction is included in a block.
        """
        tx_hash = transaction.hash
        for _ in range(timeout):
            tx = self.get_transaction_by_hash(tx_hash)
            if tx.block_number is not None:
                return tx
            time.sleep(0.1)
            with self._pending_hashes_lock:
                if len(self.pending_tx_hashes) >= 0:
                    self.generate_block()
        raise Exception(f"Transaction {tx_hash} not included in a block after {timeout} seconds")

    def wait_for_transactions(
        self, transactions: List[Transaction], timeout: int = 60
    ) -> List[TransactionByHashResponse]:
        """
        Uses `eth_getTransactionByHash` to wait for all transactions in list are included in a
        block.
        """
        tx_hashes = [tx.hash for tx in transactions]
        responses: List[TransactionByHashResponse] = []
        for _ in range(timeout):
            i = 0
            while i < len(tx_hashes):
                tx_hash = tx_hashes[i]
                tx = self.get_transaction_by_hash(tx_hash)
                if tx.block_number is not None:
                    responses.append(tx)
                    tx_hashes.pop(i)
                else:
                    i += 1
            if not tx_hashes:
                return responses
            time.sleep(0.1)
            with self._pending_hashes_lock:
                if len(self.pending_tx_hashes) >= 0:
                    self.generate_block()
        raise Exception(f"Transaction {tx_hash} not included in a block after {timeout} seconds")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(
    request, client: Client, base_genesis_header: FixtureHeader, base_fork: Fork
) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    transactions_per_block = request.config.getoption("transactions_per_block")
    return EthRPC(
        client=client,
        fork=base_fork,
        genesis_header=base_genesis_header,
        transactions_per_block=transactions_per_block,
    )
