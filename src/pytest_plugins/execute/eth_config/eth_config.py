"""Pytest plugin to test the `eth_config` RPC endpoint in a node."""

from pathlib import Path

import pytest
from pydantic import TypeAdapter

from ethereum_test_forks import Fork
from ethereum_test_rpc import EthRPC

COMMAND_EXAMPLE = """
uv run execute eth-config --chain-id 0x88bb0
 --current Prague --current-activation-time 0 --next Osaka --next-activation-time 1742999832
 --next-blob-schedule '{"baseFeeUpdateFraction": 5007716, "max": 9, "target": 6}'
"""

ForkAdapter = TypeAdapter(Fork)  # type: ignore


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    eth_config_group = parser.getgroup("execute", "Arguments defining eth_config test behavior.")
    eth_config_group.addoption(
        "--network",
        action="store",
        dest="network",
        required=True,
        type=str,
        default=None,
        help="Name of the network to verify for the RPC client.",
    )
    eth_config_group.addoption(
        "--network-file",
        action="store",
        dest="network_file",
        required=False,
        type=Path,
        default=None,
        help="Path to the yml file that contains custom network configuration.",
    )
    eth_config_group.addoption(
        "--rpc-endpoint",
        required=True,
        action="store",
        dest="rpc_endpoint",
        help="RPC endpoint to an execution client",
    )


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """Return remote RPC endpoint to be used to make requests to the execution client."""
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(rpc_endpoint: str) -> EthRPC:
    """Initialize ethereum RPC client for the execution client under test."""
    return EthRPC(rpc_endpoint)
