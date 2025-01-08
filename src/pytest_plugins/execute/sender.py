"""Sender mutex class that allows sending transactions one at a time."""

from pathlib import Path
from typing import Generator, Iterator

import pytest
from filelock import FileLock
from pytest_metadata.plugin import metadata_key  # type: ignore

from ethereum_test_base_types import Number, Wei
from ethereum_test_rpc import EthRPC
from ethereum_test_tools import EOA, Transaction


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    sender_group = parser.getgroup(
        "sender",
        "Arguments for the sender key fixtures",
    )

    sender_group.addoption(
        "--seed-account-sweep-amount",
        action="store",
        dest="seed_account_sweep_amount",
        type=Wei,
        default=None,
        help="Amount of wei to sweep from the seed account to the sender account. "
        "Default=None (Entire balance)",
    )

    sender_group.addoption(
        "--sender-funding-txs-gas-price",
        action="store",
        dest="sender_funding_transactions_gas_price",
        type=Wei,
        default=10**9,
        help=("Gas price set for the funding transactions of each worker's sender key."),
    )

    sender_group.addoption(
        "--sender-fund-refund-gas-limit",
        action="store",
        dest="sender_fund_refund_gas_limit",
        type=Wei,
        default=21_000,
        help=("Gas limit set for the funding transactions of each worker's sender key."),
    )


@pytest.fixture(scope="session")
def sender_funding_transactions_gas_price(request: pytest.FixtureRequest) -> int:
    """Get the gas price for the funding transactions."""
    return request.config.option.sender_funding_transactions_gas_price


@pytest.fixture(scope="session")
def sender_fund_refund_gas_limit(request: pytest.FixtureRequest) -> int:
    """Get the gas limit of the funding transactions."""
    return request.config.option.sender_fund_refund_gas_limit


@pytest.fixture(scope="session")
def seed_account_sweep_amount(request: pytest.FixtureRequest) -> int | None:
    """Get the seed account sweep amount."""
    return request.config.option.seed_account_sweep_amount


@pytest.fixture(scope="session")
def sender_key_initial_balance(
    seed_sender: EOA,
    eth_rpc: EthRPC,
    session_temp_folder: Path,
    worker_count: int,
    sender_funding_transactions_gas_price: int,
    sender_fund_refund_gas_limit: int,
    seed_account_sweep_amount: int | None,
) -> int:
    """
    Calculate the initial balance of each sender key.

    The way to do this is to fetch the seed sender balance and divide it by the number of
    workers. This way we can ensure that each sender key has the same initial balance.

    We also only do this once per session, because if we try to fetch the balance again, it
    could be that another worker has already sent a transaction and the balance is different.

    It's not really possible to calculate the transaction costs of each test that each worker
    is going to run, so we can't really calculate the initial balance of each sender key
    based on that.
    """
    base_name = "sender_key_initial_balance"
    base_file = session_temp_folder / base_name
    base_lock_file = session_temp_folder / f"{base_name}.lock"

    with FileLock(base_lock_file):
        if base_file.exists():
            with base_file.open("r") as f:
                sender_key_initial_balance = int(f.read())
        else:
            if seed_account_sweep_amount is None:
                seed_account_sweep_amount = eth_rpc.get_balance(seed_sender)
            seed_sender_balance_per_worker = seed_account_sweep_amount // worker_count
            assert seed_sender_balance_per_worker > 100, "Seed sender balance too low"
            # Subtract the cost of the transaction that is going to be sent to the seed sender
            sender_key_initial_balance = seed_sender_balance_per_worker - (
                sender_fund_refund_gas_limit * sender_funding_transactions_gas_price
            )

            with base_file.open("w") as f:
                f.write(str(sender_key_initial_balance))
    return sender_key_initial_balance


@pytest.fixture(scope="session")
def sender_key(
    request: pytest.FixtureRequest,
    seed_sender: EOA,
    sender_key_initial_balance: int,
    eoa_iterator: Iterator[EOA],
    eth_rpc: EthRPC,
    session_temp_folder: Path,
    sender_funding_transactions_gas_price: int,
    sender_fund_refund_gas_limit: int,
) -> Generator[EOA, None, None]:
    """
    Get the sender keys for all tests.
    """
    yield seed_sender


def pytest_sessionstart(session):  # noqa: SC200
    """Reset the sender info before the session starts."""
    session.config.stash[metadata_key]["Senders"] = {}
