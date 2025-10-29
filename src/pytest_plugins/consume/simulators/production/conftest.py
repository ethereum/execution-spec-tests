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
    import sys  # Add this import at the top

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

        for i, payload in enumerate(fixture.payloads):
            # DEBUG OUTPUT
            print(f"\n{'=' * 80}", file=sys.stderr)
            print(f"DEBUG: Checking payload {i} for test:", file=sys.stderr)
            print(f"  Test ID: {item.nodeid}", file=sys.stderr)
            print(f"  Payload type: {type(payload).__name__}", file=sys.stderr)
            print(f"  Payload attributes: {dir(payload)}", file=sys.stderr)

            if hasattr(payload, "valid"):
                print(f"  payload.valid() = {payload.valid()}", file=sys.stderr)
            else:
                print("  payload.valid() = NOT FOUND", file=sys.stderr)

            if hasattr(payload, "validation_error"):
                print(f"  payload.validation_error = {payload.validation_error}", file=sys.stderr)
            else:
                print("  payload.validation_error = NOT FOUND", file=sys.stderr)

            if hasattr(payload, "error_code"):
                print(f"  payload.error_code = {payload.error_code}", file=sys.stderr)
            else:
                print("  payload.error_code = NOT FOUND", file=sys.stderr)

            # Show params structure
            if hasattr(payload, "params") and len(payload.params) > 0:
                print(
                    f"  Transaction count: {len(payload.params[0].transactions)}", file=sys.stderr
                )

            print(f"{'=' * 80}\n", file=sys.stderr)
            # END DEBUG

            # Count transactions in this payload
            tx_count = len(payload.params[0].transactions)

            if tx_count == 0:
                has_zero_tx_payload = True
                break

            if tx_count > 1:
                has_multi_tx_payload = True
                break

            # Skip invalid payloads (we test production, not validation)
            if (
                not payload.valid()
                or payload.validation_error is not None
                or payload.error_code is not None
            ):
                print("  >>> MARKING AS INVALID <<<", file=sys.stderr)
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
            print(f"  >>> SKIPPING TEST: {item.nodeid} <<<", file=sys.stderr)
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
