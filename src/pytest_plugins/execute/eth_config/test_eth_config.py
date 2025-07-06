"""Pytest test to verify a client's configuration using `eth_config` RPC endpoint."""

import time

import pytest

from ethereum_test_rpc import EthConfigResponse, EthRPC, ForkConfig

from .networks import NETWORK_CONFIGS
from .types import NetworkConfig


@pytest.fixture(scope="session")
def eth_config_response(eth_rpc: EthRPC) -> EthConfigResponse | None:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return eth_rpc.config()


@pytest.fixture(scope="session")
def network(request: pytest.FixtureRequest) -> NetworkConfig:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return NETWORK_CONFIGS[request.config.getoption("network")]


@pytest.fixture(scope="session")
def current_time() -> int:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return int(time.time())


@pytest.fixture
def expected_current(network: NetworkConfig, current_time: int) -> ForkConfig:
    """Calculate the current fork value to verify against the client's response."""
    expected_current, _ = network.get_current_next_forks(current_time)
    return expected_current


@pytest.fixture
def expected_next(network: NetworkConfig, current_time: int) -> ForkConfig | None:
    """Calculate the next fork value to verify against the client's response."""
    _, expected_next = network.get_current_next_forks(current_time)
    return expected_next


def test_eth_config_current(
    eth_config_response: EthConfigResponse | None,
    expected_current: ForkConfig,
) -> None:
    """Validate `current` and `currentHash` field of the `eth_config` RPC endpoint."""
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
    expected_next: ForkConfig | None,
) -> None:
    """Validate `next` and `nextHash` field of the `eth_config` RPC endpoint."""
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
