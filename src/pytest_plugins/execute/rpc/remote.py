"""
Pytest plugin to run the execute in remote-rpc-mode.
"""

import pytest

from ethereum_test_base_types import Hash, Number
from ethereum_test_rpc import EthRPC
from ethereum_test_types import EOA, TransactionDefaults


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    remote_rpc_group = parser.getgroup("remote_rpc", "Arguments defining remote RPC configuration")
    remote_rpc_group.addoption(
        "--rpc-endpoint",
        required=True,
        action="store",
        dest="rpc_endpoint",
        help="RPC endpoint to an execution client",
    )
    remote_rpc_group.addoption(
        "--rpc-seed-key",
        action="store",
        required=True,
        dest="rpc_seed_key",
        help=(
            "Seed key used to fund all sender keys. This account must have a balance of at least "
            "`sender_key_initial_balance` * `workers` + gas fees. It should also be "
            "exclusively used by this command because the nonce is only checked once and if "
            "it's externally increased, the seed transactions might fail."
        ),
    )
    remote_rpc_group.addoption(
        "--rpc-chain-id",
        action="store",
        dest="rpc_chain_id",
        type=int,
        default=None,
        help="ID of the chain where the tests will be executed.",
    )
    remote_rpc_group.addoption(
        "--tx-wait-timeout",
        action="store",
        dest="tx_wait_timeout",
        type=int,
        default=60,
        help="Maximum time in seconds to wait for a transaction to be mined",
    )


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """
    Returns the remote RPC endpoint to be used to make requests to the execution client.
    """
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(request, rpc_endpoint: str) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    tx_wait_timeout = request.config.getoption("tx_wait_timeout")
    chain_id = request.config.getoption("rpc_chain_id")
    if chain_id is not None:
        TransactionDefaults.chain_id = chain_id
    return EthRPC(rpc_endpoint, transaction_wait_timeout=tx_wait_timeout)


@pytest.fixture(scope="session")
def seed_sender(request, eth_rpc: EthRPC) -> EOA:
    """
    Setup the seed sender account by checking its balance and nonce.
    """
    rpc_seed_key = Hash(request.config.getoption("rpc_seed_key"))
    # check the nonce through the rpc client
    seed_sender = EOA(key=rpc_seed_key)
    seed_sender.nonce = Number(eth_rpc.get_transaction_count(seed_sender))
    return seed_sender
