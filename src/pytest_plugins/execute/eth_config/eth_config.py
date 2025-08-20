"""Pytest plugin to test the `eth_config` RPC endpoint in a node."""

import json
import re
from hashlib import sha256
from os.path import realpath
from pathlib import Path
from typing import List, Tuple

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
    rpc_endpoint = config.getoption("rpc_endpoint")

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

        # request and store and compare all eth_config responses, then terminate
        majority_eth_config_test(exec_clients=clients, rpc_endpoint=rpc_endpoint)
        return  # TODO: how to not run the other tests, exit(1)?

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


def majority_eth_config_test(exec_clients: List[str], rpc_endpoint: str):  # noqa: D103
    # sanity checks
    assert ".ethpandaops.io" in rpc_endpoint
    assert len(exec_clients) > 0
    if "geth" in exec_clients and "devnet-3" in rpc_endpoint:
        print("Devnet-3 geth does not support eth_config")
        return

    # generate client-specific URLs from provided rpc_endpoint (it does not matter which client the original rpc_endpoint specifies)  # noqa: E501
    # we want all combinations of consensus and execution clients (sometimes an exec client is only reachable via a subset of consensus client combinations)  # noqa: E501
    pattern = r"(.*?@rpc\.)([^-]+)-([^-]+)(-.*)"
    url_dict = {
        exec_client: [
            re.sub(
                pattern,
                f"\\g<1>{consensus}-{exec_client}\\g<4>",
                rpc_endpoint,
            )
            for consensus in CONSENSUS_CLIENTS
        ]
        for exec_client in exec_clients
    }
    # url_dict looks like this:
    # {
    #     'besu': ["url for grandine+besu", "url for lighthouse+besu"], ...
    #     'erigon': ["url for grandine+erigon", "url for lighthouse+erigon"], ...
    #     ...
    # }

    # print("Majority test might contact some of these URLs:")
    # pprint(url_dict)

    # responses dict maps exec-client name to its response
    responses = dict()  # noqa: C408
    for exec_client in url_dict.keys():
        # try only as many consensus+exec client combinations until you receive a response
        # if all combinations fail we panic
        for url in url_dict[exec_client]:
            success, response = get_eth_config(url)
            if not success:
                # safely split url to not leak rpc_endpoint in logs
                print(
                    f"When trying to get eth_config from {url.split('@', 1)[-1] if '@' in url else ''} the following problem occurred: {response}"  # noqa: E501
                )
                continue

            responses[exec_client] = response
            print(f"Response of {exec_client}: {response}\n\n")
            break  # no need to gather more responses for this client

    assert len(responses.keys()) == len(exec_clients), "Failed to get an eth_config response "
    f" from each specified execution client. Full list of execution clients is {exec_clients} "
    f"but we were only able to gather eth_config responses from: {responses.keys()}\nWill try "
    "again with a different consensus-execution client combination for this execution client"

    # determine hashes of client responses
    client_to_hash_dict = dict()  # noqa: C408
    for client in responses.keys():
        response_bytes = json.dumps(responses[client], sort_keys=True).encode("utf-8")
        response_hash = sha256(response_bytes).digest().hex()
        print(f"Response hash of client {client}: {response_hash}")
        client_to_hash_dict[client] = response_hash

    # if not all responses have the same hash there is a critical consensus issue
    expected_hash = ""
    for h in client_to_hash_dict.keys():
        if expected_hash == "":
            expected_hash = client_to_hash_dict[h]
            continue

        if client_to_hash_dict[h] != expected_hash:
            pytest.exit("Critical consensus issue: Not all eth_config responses are the same!")

    print("All clients returned the same eth_config response. Test has been passed!")


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
