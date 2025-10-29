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

            # Get test_case from parameters
            test_case = item.callspec.params.get("test_case")
            if test_case is None:
                f.write("  >>> No test_case in params, skipping <<<\n")
                continue

            f.write(f"  test_case type: {type(test_case).__name__}\n")
            f.write(f"  test_case.format: {test_case.format}\n")

            # Check if this is a BlockchainEngineFixture format
            if test_case.format != BlockchainEngineFixture:
                f.write("  >>> Not BlockchainEngineFixture format, skipping <<<\n")
                continue

            f.write("  >>> Is BlockchainEngineFixture format <<<\n")

            # Now we need to actually load the fixture to check payloads
            # Get the fixtures_source from config
            fixtures_source = item.config.fixtures_source  # type: ignore[attr-defined]

            # Load the fixture the same way the test does
            from ethereum_test_fixtures.file import Fixtures

            if fixtures_source.is_stdin:
                # For stdin, fixture is already in test_case
                from ethereum_test_fixtures.consume import TestCaseStream

                if isinstance(test_case, TestCaseStream):
                    fixture = test_case.fixture
                else:
                    f.write("  >>> Can't load fixture from stdin test_case <<<\n")
                    continue
            else:
                # For file-based, load from disk
                from ethereum_test_fixtures.consume import TestCaseIndexFile

                if not isinstance(test_case, TestCaseIndexFile):
                    f.write("  >>> Not TestCaseIndexFile <<<\n")
                    continue

                fixtures_file_path = fixtures_source.path / test_case.json_path
                f.write(f"  Loading from: {fixtures_file_path}\n")

                if not fixtures_file_path.exists():
                    f.write("  >>> File doesn't exist <<<\n")
                    continue

                fixtures = Fixtures.model_validate_json(fixtures_file_path.read_text())
                fixture = fixtures[test_case.id]

            f.write(f"  Fixture loaded! Type: {type(fixture).__name__}\n")

            if not isinstance(fixture, BlockchainEngineFixture):
                f.write("  >>> Loaded fixture is not BlockchainEngineFixture <<<\n")
                continue

            f.write(f"  Number of payloads: {len(fixture.payloads)}\n")

            # Filter: only single-transaction payloads
            has_multi_tx_payload = False
            has_invalid_payload = False
            has_zero_tx_payload = False

            for i, payload in enumerate(fixture.payloads):
                f.write(f"\n  Payload {i}:\n")

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

                # Count transactions
                tx_count = len(payload.params[0].transactions)
                f.write(f"    Transaction count: {tx_count}\n")

                if tx_count == 0:
                    has_zero_tx_payload = True
                    break

                if tx_count > 1:
                    has_multi_tx_payload = True
                    break

                # Skip invalid payloads
                should_skip = False
                try:
                    if not payload.valid():
                        should_skip = True
                        f.write("    payload.valid() returned False\n")
                except:
                    pass

                if payload.validation_error is not None:
                    should_skip = True
                    f.write("    Has validation_error\n")

                if payload.error_code is not None:
                    should_skip = True
                    f.write("    Has error_code\n")

                if should_skip:
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
