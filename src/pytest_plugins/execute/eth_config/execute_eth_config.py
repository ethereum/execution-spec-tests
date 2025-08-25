"""Pytest test to verify a client's configuration using `eth_config` RPC endpoint."""

import json
import time
from hashlib import sha256
from typing import Dict, List

import pytest

from ethereum_test_rpc import EthConfigResponse, EthRPC

from .eth_config import get_rpc_url_combinations_el_cl, request_eth_config
from .types import NetworkConfig


@pytest.fixture(scope="session")
def eth_config_response(eth_rpc: EthRPC) -> EthConfigResponse | None:
    """Get the `eth_config` response from the client to be verified by all tests."""
    return eth_rpc.config(timeout=10)


@pytest.fixture(scope="session")
def network(request) -> NetworkConfig:
    """Get the network that will be used to verify all tests."""
    config = request.config
    return config.getoption("network")


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
    request,
) -> None:
    """Validate `current` field of the `eth_config` RPC endpoint."""
    config = request.config
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    assert eth_config_response.current is not None, (
        "Client did not return a valid `current` fork config."
    )
    expected_current = expected_eth_config.current
    assert eth_config_response.current == expected_current, (
        "Client's `current` fork config does not match expected value: "
        f"{eth_config_response.current.model_dump_json(indent=2)} != "
        f"{expected_current.model_dump_json(indent=2)}"
    )


def test_eth_config_current_fork_id(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
    request,
) -> None:
    """Validate `forkId` field within the `current` configuration object."""
    config = request.config
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    assert eth_config_response.current is not None, (
        "Client did not return a valid `current` fork config."
    )
    assert eth_config_response.current.fork_id is not None, (
        "Client did not return a valid `forkId` in the current fork config."
    )
    assert eth_config_response.current.fork_id == expected_eth_config.current.fork_id, (
        "Client's `current.forkId` does not match expected value: "
        f"{eth_config_response.current.fork_id} != "
        f"{expected_eth_config.current.fork_id}"
    )


def test_eth_config_next(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
    request,
) -> None:
    """Validate `next` field of the `eth_config` RPC endpoint."""
    config = request.config
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    expected_next = expected_eth_config.next
    if expected_next is None:
        assert eth_config_response.next is None, (
            "Client returned a `next` fork config but expected None."
        )
    else:
        assert eth_config_response.next is not None, (
            "Client did not return a valid `next` fork config."
        )
        assert eth_config_response.next == expected_next, (
            "Client's `next` fork config does not match expected value: "
            f"{eth_config_response.next.model_dump_json(indent=2)} != "
            f"{expected_next.model_dump_json(indent=2)}"
        )


def test_eth_config_next_fork_id(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
    request,
) -> None:
    """Validate `forkId` field within the `next` configuration object."""
    config = request.config
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    expected_next = expected_eth_config.next
    if expected_next is None:
        assert eth_config_response.next is None, (
            "Client returned a `next` fork config but expected None."
        )
    else:
        assert eth_config_response.next is not None, (
            "Client did not return a valid `next` fork config."
        )
        expected_next_fork_id = expected_next.fork_id
        if expected_next_fork_id is None:
            assert eth_config_response.next.fork_id is None, (
                "Client returned a `next.forkId` but expected None."
            )
        else:
            received_fork_id = eth_config_response.next.fork_id
            assert received_fork_id is not None, "Client did not return a valid `next.forkId`."
            assert received_fork_id == expected_next_fork_id, (
                "Client's `next.forkId` does not match expected value: "
                f"{received_fork_id} != "
                f"{expected_next_fork_id}"
            )


def test_eth_config_last(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
    config: pytest.Config,
) -> None:
    """Validate `last` field of the `eth_config` RPC endpoint."""
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    expected_last = expected_eth_config.last
    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    if expected_last is None:
        assert eth_config_response.last is None, (
            "Client returned a `last` fork config but expected None."
        )
    else:
        assert eth_config_response.last is not None, (
            "Client did not return a valid `last` fork config."
        )
        assert eth_config_response.last == expected_last, (
            "Client's `last` fork config does not match expected value: "
            f"{eth_config_response.last.model_dump_json(indent=2)} != "
            f"{expected_last.model_dump_json(indent=2)}"
        )


def test_eth_config_last_fork_id(
    eth_config_response: EthConfigResponse | None,
    expected_eth_config: EthConfigResponse,
    config: pytest.Config,
) -> None:
    """Validate `forkId` field within the `last` configuration object."""
    if config.getoption("network_config_file") is None:
        pytest.skip("Skipping test because no 'network_config_file' was specified")

    assert eth_config_response is not None, "Client did not return a valid `eth_config` response."
    expected_last = expected_eth_config.last
    if expected_last is None:
        assert eth_config_response.last is None, (
            "Client returned a `last` fork config but expected None."
        )
    else:
        assert eth_config_response.last is not None, (
            "Client did not return a valid `last` fork config."
        )
        expected_last_fork_id = expected_last.fork_id
        if expected_last_fork_id is None:
            assert eth_config_response.last.fork_id is None, (
                "Client returned a `last.forkId` but expected None."
            )
        else:
            received_fork_id = eth_config_response.last.fork_id
            assert received_fork_id is not None, "Client did not return a valid `last.forkId`."
            assert received_fork_id == expected_last_fork_id, (
                "Client's `last.forkId` does not match expected value: "
                f"{received_fork_id} != "
                f"{expected_last_fork_id}"
            )


def test_eth_config_majority(
    request,
) -> None:
    """Queries devnet exec clients for their eth_config and fails if not all have the same response."""  # noqa: E501
    # decide whether to run this test
    config = request.config
    run_this_test_bool = config.getoption(name="majority_eth_config_test_enabled")
    if not run_this_test_bool:
        pytest.skip("Skipping eth_config majority test")

    # retrieve required values for running this test
    rpc_endpoint = config.getoption("rpc_endpoint")
    el_clients: List[str] = config.getoption("majority_clients")  # besu, erigon, ..

    url_dict: None | Dict[str, List[str]] = get_rpc_url_combinations_el_cl(
        el_clients=el_clients, rpc_endpoint=rpc_endpoint
    )
    assert url_dict is not None

    responses = dict()  # noqa: C408
    for exec_client in url_dict.keys():
        # try only as many consensus+exec client combinations until you receive a response
        # if all combinations fail we panic
        for url in url_dict[exec_client]:
            success, response = request_eth_config(url=url, timeout=9)
            if not success:
                # safely split url to not leak rpc_endpoint in logs
                print(
                    f"When trying to get eth_config from {url.split('@', 1)[-1] if '@' in url else ''} the following problem occurred: {response}"  # noqa: E501
                )
                continue

            responses[exec_client] = response
            print(f"Response of {exec_client}: {response}\n\n")
            break  # no need to gather more responses for this client

    assert len(responses.keys()) == len(el_clients), "Failed to get an eth_config response "
    f" from each specified execution client. Full list of execution clients is {el_clients} "
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

        assert client_to_hash_dict[h] == expected_hash, (
            "Critical consensus issue: Not all eth_config responses are the same!"
        )
    assert expected_hash != ""

    print("All clients returned the same eth_config response. Test has been passed!")
