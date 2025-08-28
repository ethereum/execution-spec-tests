"""Pytest plugin to test the `eth_config` RPC endpoint in a node."""

from os.path import realpath
from pathlib import Path

import pytest
import requests

from ethereum_test_rpc import EthRPC

from .types import Genesis, NetworkConfigFile

CURRENT_FILE = Path(realpath(__file__))
CURRENT_FOLDER = CURRENT_FILE.parent

DEFAULT_NETWORK_CONFIGS_FILE = CURRENT_FOLDER / "networks.yml"
DEFAULT_NETWORKS = NetworkConfigFile.from_yaml(DEFAULT_NETWORK_CONFIGS_FILE)


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    eth_config_group = parser.getgroup("execute", "Arguments defining eth_config test behavior.")
    eth_config_group.addoption(
        "--network",
        action="store",
        dest="network",
        required=False,
        type=str,
        default=None,
        help=(
            "Name of the network to verify for the RPC client. Supported networks by default: "
            f"{', '.join(DEFAULT_NETWORKS.root.keys())}."
        ),
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
        "--genesis-config-file",
        action="store",
        dest="genesis_config_file",
        required=False,
        type=Path,
        default=None,
        help="Path to a genesis JSON file from which a custom network configuration "
        "must be derived.",
    )
    eth_config_group.addoption(
        "--genesis-config-url",
        action="store",
        dest="genesis_config_url",
        required=False,
        type=str,
        default=None,
        help="URL to a genesis JSON file from which a custom network configuration "
        "must be derived.",
    )
    eth_config_group.addoption(
        "--rpc-endpoint",
        required=True,
        action="store",
        dest="rpc_endpoint",
        help="RPC endpoint to the execution client that will be tested.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """
    Load the network configuration file and load the specific network to be used for
    the test.
    """
    genesis_config_file = config.getoption("genesis_config_file")
    genesis_config_url = config.getoption("genesis_config_url")
    network_configs_path = config.getoption("network_config_file", default=None)
    network_name = config.getoption("network")

    if genesis_config_file and genesis_config_url:
        pytest.exit(
            "Cannot specify both the --genesis-config-file and --genesis-config-url flags."
        )

    if (genesis_config_file or genesis_config_url) and network_name:
        pytest.exit(
            "Cannot specify a network name when using the --genesis-config-file or "
            "--genesis-config-url flag."
        )
    # handle the one of the three flags that was passed
    #   case 1: genesis_config_file
    if genesis_config_file:
        genesis_config_contents = genesis_config_file.read_text()
        genesis_config = Genesis.model_validate_json(genesis_config_contents)
        config.network = genesis_config.network_config()  # type: ignore
    #   case 2: genesis_config_url
    elif genesis_config_url:
        genesis_config_contents = requests.get(genesis_config_url).text
        genesis_config = Genesis.model_validate_json(genesis_config_contents)
        config.network = genesis_config.network_config()  # type: ignore
    #   case 3: network_name
    elif network_name:
        # load provided networks file
        if network_configs_path is None:
            network_configs_path = DEFAULT_NETWORK_CONFIGS_FILE
        if not network_configs_path.exists():
            pytest.exit(f'Specified networks file "{network_configs_path}" does not exist.')
        try:
            network_configs = NetworkConfigFile.from_yaml(network_configs_path)
        except Exception as e:
            pytest.exit(f"Could not load file {network_configs_path}: {e}")

        if network_name not in network_configs.root:
            pytest.exit(
                f'Network "{network_name}" could not be found in file "{network_configs_path}".'
            )
        config.network = network_configs.root[network_name]  # type: ignore

    if config.getoption("collectonly", default=False):
        return

    # Test out the RPC endpoint to be able to fail fast if it's not working
    eth_rpc = EthRPC(config.getoption("rpc_endpoint"))
    try:
        eth_rpc.chain_id()
    except Exception as e:
        pytest.exit(f"Could not connect to RPC endpoint {config.getoption('rpc_endpoint')}: {e}")
    try:
        eth_rpc.config()
    except Exception as e:
        pytest.exit(
            f"RPC endpoint {config.getoption('rpc_endpoint')} does not support `eth_config`: {e}"
        )


@pytest.fixture(autouse=True, scope="session")
def rpc_endpoint(request) -> str:
    """Return remote RPC endpoint to be used to make requests to the execution client."""
    return request.config.getoption("rpc_endpoint")


@pytest.fixture(autouse=True, scope="session")
def eth_rpc(rpc_endpoint: str) -> EthRPC:
    """Initialize ethereum RPC client for the execution client under test."""
    return EthRPC(rpc_endpoint)
