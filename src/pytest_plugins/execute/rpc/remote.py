"""
Pytest plugin to run the execute in remote-rpc-mode.
"""

from urllib.parse import urlparse

import pytest

from ethereum_test_tools import EOA, Address
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
    parsed_url = urlparse(rpc_endpoint)
    hostname = parsed_url.hostname
    assert hostname is not None, "invalid eth_rpc endpoint provided"
    port = parsed_url.port
    if port is not None:
        return EthRPC(ip=hostname, port=port)
    return EthRPC(ip=hostname)


@pytest.fixture(scope="session")
def seed_sender(request, eth_rpc: EthRPC) -> EOA:
    """
    Setup the seed sender account by checking its balance and nonce.
    """
    rpc_seed_key = Address(request.config.getoption("rpc_seed_key"))
    # check the nonce through the rpc client
    nonce = eth_rpc.get_transaction_count(rpc_seed_key)
    seed_sender = EOA(rpc_seed_key, nonce=nonce)
    return seed_sender
