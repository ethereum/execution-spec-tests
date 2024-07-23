"""
Pytest plugin to run the execute in remote-rpc-mode.
"""

import pytest

from ethereum_test_base_types import Number
from ethereum_test_tools import EOA, Hash
from ethereum_test_tools.rpc import EthRPC


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    remote_rpc_group = parser.getgroup("remote_rpc", "Arguments defining remote RPC configuration")
    remote_rpc_group.addoption(
        "--rpc-endpoint",
        action="store",
        dest="rpc_endpoint",
        help="RPC endpoint to an execution client",
    )
    remote_rpc_group.addoption(
        "--rpc-seed-key",
        action="store",
        dest="rpc_seed_key",
        help=(
            "Seed key used to fund all sender keys. This account must have a balance of at least "
            "`sender_key_initial_balance` * `sender_key_count` + gas fees. It should also be "
            "exclusively used by this command because the nonce is only checked once and if "
            "it's externally increased, the seed transactions might fail."
        ),
    )


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """
    Returns the remote RPC endpoint to be used to make requests to the execution client.
    """
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(rpc_endpoint: str) -> EthRPC:
    """
    Initialize ethereum RPC client for the execution client under test.
    """
    return EthRPC(rpc_endpoint)


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
