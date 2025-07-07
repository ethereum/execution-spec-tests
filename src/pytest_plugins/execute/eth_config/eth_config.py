"""Pytest plugin to test the `eth_config` RPC endpoint in a node."""

from os.path import realpath
from pathlib import Path

import pytest

from ethereum_test_rpc import EthRPC

from .types import NetworkConfigFile

CURRENT_FILE = Path(realpath(__file__))
CURRENT_FOLDER = CURRENT_FILE.parent


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
        "--network-config-file",
        action="store",
        dest="network_config_file",
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


DEFAULT_NETWORK_CONFIGS_FILE = CURRENT_FOLDER / "networks.yml"


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """
    Load the network configuration file and load the specific network to be used for
    the test.
    """
    network_configs_path = config.getoption("network_config_file", default=None)
    if network_configs_path is None:
        network_configs_path = DEFAULT_NETWORK_CONFIGS_FILE
    if not network_configs_path.exists():
        pytest.exit(f'Specified networks file "{network_configs_path}" does not exist.')
    try:
        network_configs = NetworkConfigFile.from_yaml(network_configs_path)
    except Exception as e:
        pytest.exit(f"Could not load file {network_configs_path}: {e}")
    network_name = config.getoption("network")
    if network_name not in network_configs.root:
        pytest.exit(
            f'Network "{network_name}" could not be found in file "{network_configs_path}".'
        )
    config.network = network_configs.root[network_name]  # type: ignore


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """Return remote RPC endpoint to be used to make requests to the execution client."""
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(rpc_endpoint: str) -> EthRPC:
    """Initialize ethereum RPC client for the execution client under test."""
    return EthRPC(rpc_endpoint)
