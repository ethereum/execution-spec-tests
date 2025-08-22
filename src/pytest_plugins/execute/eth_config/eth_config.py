"""Pytest plugin to test the `eth_config` RPC endpoint in a node."""

import re
from os.path import realpath
from pathlib import Path
from typing import Dict, List, Tuple

import pytest
import requests

from ethereum_test_rpc import EthRPC

from .types import NetworkConfigFile

CURRENT_FILE = Path(realpath(__file__))
CURRENT_FOLDER = CURRENT_FILE.parent

DEFAULT_NETWORK_CONFIGS_FILE = CURRENT_FOLDER / "networks.yml"
DEFAULT_NETWORKS = NetworkConfigFile.from_yaml(DEFAULT_NETWORK_CONFIGS_FILE)

EXECUTION_CLIENTS = ["besu", "erigon", "geth", "nethermind", "reth"]
CONSENSUS_CLIENTS = ["grandine", "lighthouse", "lodestar", "nimbus", "prysm", "teku"]


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
        help="Path to the yml file that contains custom network configuration "
        "(e.g. ./src/pytest_plugins/execute/eth_config/networks.yml).\nIf no config is provided "
        "then majority mode will be used for devnet testing (clients that have a different "
        "response than the majority of clients will fail the test)",
    )
    eth_config_group.addoption(
        "--clients",
        required=False,
        action="store",
        dest="clients",
        type=str,
        default="besu,erigon,geth,nethermind,reth",
        help="Comma-separated list of clients to be tested in majority mode. This flag will be "
        "ignored when you pass a value for the network-config-file flag. Default: "
        "besu,erigon,geth,nethermind,reth",
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
    # get flag values
    network_name = config.getoption("network")
    network_configs_path = config.getoption("network_config_file")
    clients = config.getoption("clients")

    # set flags for defining whether to run majority eth_config test or not, and how
    config.option.majority_eth_config_test_enabled = False
    config.option.majority_clients = []  # List[str]

    # either load network file or activate majority test mode
    if network_configs_path is not None:  # case 1: load provided networks file
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
    else:  # case 2: activate majority test mode
        #   parse clients list
        clients.replace(" ", "")
        clients = clients.split(",")
        for c in clients:
            if c not in EXECUTION_CLIENTS:
                pytest.exit(f"Unsupported client was passed: {c}")
        print(f"Activating majority mode\nProvided client list: {clients}")

        # store majority mode configuration
        config.option.majority_eth_config_test_enabled = True
        config.option.majority_clients = clients  # List[str]

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


def get_eth_config(url: str) -> Tuple[bool, str]:  # success, response
    """Request data from devnet node via JSON_RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_config",
        "params": [],
        "id": 1,
    }

    headers = {"Content-Type": "application/json"}

    try:
        # Make the request
        response = requests.post(url, json=payload, headers=headers, timeout=20)

        # Return JSON response
        return True, response.json()

    except Exception as e:
        return False, f"error: {e}"


def get_rpc_url_combinations_el_cl(
    el_clients: List[str], rpc_endpoint: str
) -> None | Dict[str, List[str]]:
    """Get cl+el url combinations for json rpc."""
    # sanity checks
    assert ".ethpandaops.io" in rpc_endpoint
    assert len(el_clients) > 0
    if "geth" in el_clients and "fusaka-devnet-3" in rpc_endpoint:
        print("fusaka-devnet-3 geth does not support eth_config")
        return None

    # generate client-specific URLs from provided rpc_endpoint (it does not matter which client the original rpc_endpoint specifies)  # noqa: E501
    # we want all combinations of consensus and execution clients (sometimes an exec client is only reachable via a subset of consensus client combinations)  # noqa: E501
    pattern = r"(.*?@rpc\.)([^-]+)-([^-]+)(-.*)"
    url_dict: Dict[str, List[str]] = {
        exec_client: [
            re.sub(
                pattern,
                f"\\g<1>{consensus}-{exec_client}\\g<4>",
                rpc_endpoint,
            )
            for consensus in CONSENSUS_CLIENTS
        ]
        for exec_client in el_clients
    }
    # url_dict looks like this:
    # {
    #     'besu': ["url for grandine+besu", "url for lighthouse+besu"], ...
    #     'erigon': ["url for grandine+erigon", "url for lighthouse+erigon"], ...
    #     ...
    # }

    return url_dict
