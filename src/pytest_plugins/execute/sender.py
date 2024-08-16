"""
Sender mutex class that allows sending transactions one at a time.
"""
from pathlib import Path
from typing import Generator, Iterator

import pytest
from filelock import FileLock

from ethereum_test_base_types import Number
from ethereum_test_rpc import EthRPC
from ethereum_test_tools import EOA, Transaction


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    senders_group = parser.getgroup(
        "senders", "Arguments defining sender keys used to fund tests."
    )
    senders_group.addoption(
        "--sender-key-initial-balance",
        action="store",
        dest="sender_key_initial_balance",
        type=int,
        default=10**26,
        help=(
            "Initial balance of each sender key. There is one sender key per worker process "
            "(`-n` option)."
        ),
    )


@pytest.fixture(scope="session")
def sender_key(
    request,
    seed_sender: EOA,
    eoa_iterator: Iterator[EOA],
    eth_rpc: EthRPC,
    session_temp_folder: Path,
) -> Generator[EOA, None, None]:
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

    sender = next(eoa_iterator)
    # fund all sender keys
    sender_key_initial_balance = request.config.getoption("sender_key_initial_balance")

    with FileLock(seed_sender_lock_file):
        if seed_sender_nonce_file.exists():
            with seed_sender_nonce_file.open("r") as f:
                seed_sender.nonce = Number(f.read())
        fund_tx = Transaction(
            sender=seed_sender,
            to=sender,
            gas_limit=21_000,
            gas_price=10**9,
            value=sender_key_initial_balance,
        ).with_signature_and_sender()
        eth_rpc.send_transaction(fund_tx)
        with seed_sender_nonce_file.open("w") as f:
            f.write(str(seed_sender.nonce))
    eth_rpc.wait_for_transaction(fund_tx)

    yield sender

    # refund all sender keys
    remaining_balance = eth_rpc.get_balance(sender)
    refund_gas_limit = 21_000
    refund_gas_price = 10**9
    tx_cost = refund_gas_limit * refund_gas_price

    if remaining_balance < tx_cost:
        return

    refund_tx = Transaction(
        sender=sender,
        to=seed_sender,
        gas_limit=21_000,
        gas_price=10**9,
        value=remaining_balance - tx_cost,
    ).with_signature_and_sender()

    eth_rpc.send_wait_transaction(refund_tx)
