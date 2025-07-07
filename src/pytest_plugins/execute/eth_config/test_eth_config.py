"""Pytest test to verify a client's configuration using `eth_config` RPC endpoint."""

import time
from os.path import realpath
from pathlib import Path

import pytest

from ethereum_test_rpc import EthConfigResponse, EthRPC, ForkConfig

from .types import NetworkConfig, NetworkConfigFile

CURRENT_FILE = Path(realpath(__file__))
CURRENT_FOLDER = CURRENT_FILE.parent

DEFAULT_NETWORK_CONFIGS_FILE = CURRENT_FOLDER / "networks.yml"


@pytest.fixture(scope="session")
def eth_config_response(eth_rpc: EthRPC) -> EthConfigResponse | None:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return eth_rpc.config()


@pytest.fixture(scope="session")
def network_configs_path(request: pytest.FixtureRequest) -> Path:
    """Get the path to the networks config file to be used."""
    network_configs_file = request.config.getoption("network_file")
    if network_configs_file is None:
        return DEFAULT_NETWORK_CONFIGS_FILE
    else:
        return network_configs_file


@pytest.fixture(scope="session")
def network_configs(network_configs_path: Path) -> NetworkConfigFile:
    """Get the file contents from the provided network configs file."""
    return NetworkConfigFile.from_yaml(network_configs_path)


@pytest.fixture(scope="session")
def network(
    request: pytest.FixtureRequest, network_configs: NetworkConfigFile, network_configs_path: Path
) -> NetworkConfig:
    """Get the `eth_config` response from the client to be verified by all tests."""
    network_name = request.config.getoption("network")
    assert network_name in network_configs.root, (
        f"Network {network_name} could not be found in file {network_configs_path}"
    )
    return network_configs.root[network_name]


@pytest.fixture(scope="session")
def current_time() -> int:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return int(time.time())


@pytest.fixture(scope="session")
def expected_eth_config(network: NetworkConfig, current_time: int) -> EthConfigResponse:
    """Calculate the current fork value to verify against the client's response."""
    return network.get_eth_config(current_time)


def test_eth_config_current(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
) -> None:
    """Validate `current` and `currentHash` field of the `eth_config` RPC endpoint."""
    expected_current = expected_eth_config.current
    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    assert eth_config_response.current is not None, (
        "Client did not return a valid `current` fork config."
    )
    assert eth_config_response.current_hash is not None, (
        "Client did not return a valid `currentHash` fork config hash."
    )
    assert eth_config_response.current == expected_current, (
        "Client's `current` fork config does not match expected value."
    )
    assert eth_config_response.current_hash == expected_current.get_hash(), (
        "Client's `currentHash` fork config hash does not match expected value."
    )


def test_eth_config_next(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
) -> None:
    """Validate `next` and `nextHash` field of the `eth_config` RPC endpoint."""
    expected_next: ForkConfig | None = expected_eth_config.next
    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    if expected_next is None:
        assert eth_config_response.next is None, (
            "Client returned a `next` fork config but expected None."
        )
        assert eth_config_response.next_hash is None, (
            "Client returned a `nextHash` fork config hash but expected None."
        )
    else:
        assert eth_config_response.next is not None, (
            "Client did not return a valid `next` fork config."
        )
        assert eth_config_response.next == expected_next, (
            "Client's `next` fork config does not match expected value."
        )
        assert eth_config_response.next_hash == expected_next.get_hash(), (
            "Client's `nextHash` fork config hash does not match expected value."
        )
