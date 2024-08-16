"""
Sender mutex class that allows sending transactions one at a time.
"""
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Generator, Iterator, List

import pytest
from filelock import FileLock

from ethereum_test_base_types import Number
from ethereum_test_rpc import EthRPC
from ethereum_test_tools import EOA, Transaction


class SenderLock:
    """
    Simple sender key with a mutex.
    """

    sender: EOA
    _lock: Lock

    def __init__(self, sender: EOA):
        """
        Initialize the sender with a lock
        """
        self.sender = sender
        self._lock = Lock()


class Senders:
    """
    Class to obtain the next free sender.
    """

    senders: List[SenderLock]

    def __init__(self, senders: List[EOA]):
        """
        Initialize the senders with a lock
        """
        self.senders = [SenderLock(sender) for sender in senders]

    def __iter__(self):
        """
        Return the senders.
        """
        return iter(self.senders)

    @contextmanager
    def get_sender(self) -> Generator[EOA, None, None]:
        """
        Return the next free sender and lock it.
        """
        while True:
            for sender in self.senders:
                if sender._lock.acquire(blocking=False):
                    yield sender.sender
                    sender._lock.release()
                    return
            time.sleep(0)


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    senders_group = parser.getgroup(
        "senders", "Arguments defining sender keys used to fund tests."
    )
    senders_group.addoption(
        "--sender-key-count",
        action="store",
        dest="sender_key_count",
        type=int,
        default=1,
        help=("Number of sender keys to fund on genesis."),
    )
    senders_group.addoption(
        "--sender-key-initial-balance",
        action="store",
        dest="sender_key_initial_balance",
        type=int,
        default=10**26,
        help=("Initial balance of each sender key."),
    )


@pytest.fixture(scope="session")
def sender_keys(
    request,
    seed_sender: EOA,
    eoa_iterator: Iterator[EOA],
    eth_rpc: EthRPC,
    session_temp_folder: Path,
) -> Generator[Senders, None, None]:
    """
    Get the sender keys for all tests.

    The seed sender is going to be shared among different processes, so we need to lock it
    before we produce each funding transaction.
    """
    # For the seed sender we do need to keep track of the nonce because it is shared among
    # different processes, and there might not be a new block produced between the transactions.
    seed_sender_nonce_file_name = "seed_sender_nonce"
    seed_sender_lock_file_name = f"{seed_sender_nonce_file_name}.lock"
    seed_sender_nonce_file = session_temp_folder / seed_sender_nonce_file_name
    seed_sender_lock_file = session_temp_folder / seed_sender_lock_file_name

    sender_key_count = request.config.getoption("sender_key_count")
    senders = Senders([next(eoa_iterator) for _ in range(sender_key_count)])
    # fund all sender keys
    sender_key_initial_balance = request.config.getoption("sender_key_initial_balance")

    with FileLock(seed_sender_lock_file):
        if seed_sender_nonce_file.exists():
            with seed_sender_nonce_file.open("r") as f:
                seed_sender.nonce = Number(f.read())
        fund_txs = [
            Transaction(
                sender=seed_sender,
                to=sender.sender,
                gas_limit=21_000,
                gas_price=10**9,
                value=sender_key_initial_balance,
            ).with_signature_and_sender()
            for sender in senders
        ]
        eth_rpc.send_transactions(fund_txs)
        with seed_sender_nonce_file.open("w") as f:
            f.write(str(seed_sender.nonce))
    eth_rpc.wait_for_transactions(fund_txs)
    yield senders
    # refund all sender keys
    refund_txs: List[Transaction] = []
    for sender in senders:
        remaining_balance = eth_rpc.get_balance(sender.sender)
        refund_gas_limit = 21_000
        refund_gas_price = 10**9
        tx_cost = refund_gas_limit * refund_gas_price
        if remaining_balance < tx_cost:
            continue
        refund_txs.append(
            Transaction(
                sender=sender.sender,
                to=seed_sender,
                gas_limit=21_000,
                gas_price=10**9,
                value=remaining_balance - tx_cost,
            ).with_signature_and_sender()
        )
    eth_rpc.send_wait_transactions(refund_txs)
