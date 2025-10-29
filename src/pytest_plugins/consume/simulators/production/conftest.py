"""
Pytest fixtures for the `consume production` simulator.

Tests block PRODUCTION (not just validation) by having clients build blocks
from mempool transactions using forkchoiceUpdated + getPayload.
"""

import io
import logging
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
logger = logging.getLogger(__name__)


def pytest_configure(config: pytest.Config) -> None:
    """Set the supported fixture formats for the production simulator."""
    config.supported_fixture_formats = [BlockchainEngineFixture]  # type: ignore[attr-defined]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Filter out tests that don't meet production simulator requirements.
    """
    with open("/tmp/production_filter_debug.log", "w") as f:
        f.write("=" * 80 + "\n")
        f.write("COLLECTION PHASE STARTING\n")
        f.write("=" * 80 + "\n\n")

        for item in items:
            if not hasattr(item, "callspec"):
                continue

            # Check the actual function being called
            test_function_name = item.function.__name__ if hasattr(item, "function") else None

            # Only process if this is a production test
            if test_function_name != "test_blockchain_via_production":
                continue

            f.write(f"\nTest: {item.nodeid}\n")
            f.write(f"  Function name: {test_function_name}\n")

            # Get the fixture from parameters
            f.write(f"  Callspec params: {item.callspec.params.keys()}\n")
            fixture = item.callspec.params.get("fixture")

            f.write(f"  Fixture type: {type(fixture)}\n")
            f.write(f"  Fixture class name: {type(fixture).__name__}\n")
            f.write(
                f"  Is BlockchainEngineFixture: {isinstance(fixture, BlockchainEngineFixture)}\n"
            )

            if not isinstance(fixture, BlockchainEngineFixture):
                f.write("  >>> Not BlockchainEngineFixture, skipping <<<\n")
                continue

            f.write("  >>> Has BlockchainEngineFixture <<<\n")
            f.write(f"  Number of payloads: {len(fixture.payloads)}\n")

            # Filter: only single-transaction payloads
            has_multi_tx_payload = False
            has_invalid_payload = False
            has_zero_tx_payload = False

            for i, payload in enumerate(fixture.payloads):
                f.write(f"\n  Payload {i}:\n")
                f.write(f"    Type: {type(payload).__name__}\n")

                if hasattr(payload, "valid"):
                    try:
                        valid_result = payload.valid()
                        f.write(f"    payload.valid() = {valid_result}\n")
                    except Exception as e:
                        f.write(f"    payload.valid() ERROR: {e}\n")

                if hasattr(payload, "validation_error"):
                    f.write(f"    payload.validation_error = {payload.validation_error}\n")

                if hasattr(payload, "error_code"):
                    f.write(f"    payload.error_code = {payload.error_code}\n")

                # Count transactions in this payload
                tx_count = len(payload.params[0].transactions)
                f.write(f"    Transaction count: {tx_count}\n")

                if tx_count == 0:
                    has_zero_tx_payload = True
                    break

                if tx_count > 1:
                    has_multi_tx_payload = True
                    break

                # Skip invalid payloads
                if (
                    not payload.valid()
                    or payload.validation_error is not None
                    or payload.error_code is not None
                ):
                    f.write("    >>> MARKING AS INVALID <<<\n")
                    has_invalid_payload = True
                    break

            if has_zero_tx_payload:
                f.write("\n  >>> WILL SKIP: zero transactions <<<\n")
                item.add_marker(
                    pytest.mark.skip(
                        reason="Production simulator: zero-transaction payloads not supported"
                    )
                )
            elif has_multi_tx_payload:
                f.write("\n  >>> WILL SKIP: multiple transactions <<<\n")
                item.add_marker(
                    pytest.mark.skip(
                        reason="Production simulator: multi-transaction payloads not supported"
                    )
                )
            elif has_invalid_payload:
                f.write("\n  >>> WILL SKIP: invalid payload <<<\n")
                item.add_marker(
                    pytest.mark.skip(
                        reason="Production simulator: only tests valid block production"
                    )
                )
            else:
                f.write("\n  >>> TEST WILL RUN <<<\n")


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
