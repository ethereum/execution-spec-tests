"""
Pytest fixtures for the `consume production` simulator.

Tests block PRODUCTION (not just validation) by having clients build blocks
from mempool transactions using forkchoiceUpdated + getPayload.
"""

import io
from typing import Mapping

import pytest
from hive.client import Client

from ethereum_test_exceptions import ExceptionMapper
from ethereum_test_fixtures import BlockchainEngineFixture
from ethereum_test_rpc import EngineRPC

pytest_plugins = (
    "pytest_plugins.pytest_hive.pytest_hive",
    "pytest_plugins.consume.simulators.base",
    "pytest_plugins.consume.simulators.single_test_client",
    "pytest_plugins.consume.simulators.test_case_description",
    "pytest_plugins.consume.simulators.timing_data",
    "pytest_plugins.consume.simulators.exceptions",
)


def pytest_configure(config: pytest.Config) -> None:
    """Set the supported fixture formats for the production simulator."""
    config.supported_fixture_formats = [BlockchainEngineFixture]  # type: ignore[attr-defined]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Filter out tests that don't meet production simulator requirements.

    Requirements:
    - Must have exactly one transaction per payload (no multi-tx blocks)
    - Payload must be valid (we're testing production, not validation)
    """
    for item in items:
        if not hasattr(item, "callspec"):
            continue

        # Only process if this is a production test
        if "test_blockchain_via_production" not in item.nodeid:
            continue

        # Get the fixture from parameters
        fixture = item.callspec.params.get("fixture")
        if not isinstance(fixture, BlockchainEngineFixture):
            continue

        # Filter: only single-transaction payloads
        has_multi_tx_payload = False
        has_invalid_payload = False
        has_zero_tx_payload = False

        for payload in fixture.payloads:
            # Count transactions in this payload
            tx_count = len(payload.params[0].transactions)

            if tx_count == 0:
                has_zero_tx_payload = True
                break

            if tx_count > 1:
                has_multi_tx_payload = True
                break

            # Skip invalid payloads (we test production, not validation)
            if not payload.valid():
                has_invalid_payload = True
                break

        if has_zero_tx_payload:
            item.add_marker(
                pytest.mark.skip(
                    reason="Production simulator: zero-transaction payloads not supported"
                )
            )
        elif has_multi_tx_payload:
            item.add_marker(
                pytest.mark.skip(
                    reason="Production simulator: multi-transaction payloads not supported"
                )
            )
        elif has_invalid_payload:
            item.add_marker(
                pytest.mark.skip(reason="Production simulator: only tests valid block production")
            )


@pytest.fixture(scope="function")
def engine_rpc(client: Client, client_exception_mapper: ExceptionMapper | None) -> EngineRPC:
    """Initialize engine RPC client for the execution client under test."""
    if client_exception_mapper:
        return EngineRPC(
            f"http://{client.ip}:8551",
            response_validation_context={
                "exception_mapper": client_exception_mapper,
            },
        )
    return EngineRPC(f"http://{client.ip}:8551")


@pytest.fixture(scope="module")
def test_suite_name() -> str:
    """The name of the hive test suite used in this simulator."""
    return "eest/consume-production"


@pytest.fixture(scope="module")
def test_suite_description() -> str:
    """The description of the hive test suite used in this simulator."""
    return (
        "Test block PRODUCTION (not validation) by having clients build blocks from "
        "mempool transactions using forkchoiceUpdated + getPayload flow."
    )


@pytest.fixture(scope="function")
def client_files(buffered_genesis: io.BufferedReader) -> Mapping[str, io.BufferedReader]:
    """Define the files that hive will start the client with."""
    files = {}
    files["/genesis.json"] = buffered_genesis
    return files
