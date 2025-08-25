"""
Pytest plugin for witness functionality.

Provides --witness command-line option that installs the witness-filler tool
and generates execution witness data for blockchain test fixtures when enabled.
"""

import subprocess
from typing import Any, Callable, List

import pytest

from ethereum_test_base_types import EthereumTestRootModel
from ethereum_test_fixtures.blockchain import FixtureBlock, WitnessChunk


class WitnessFillerResult(EthereumTestRootModel[List[WitnessChunk]]):
    """Model that defines the expected result from the `witness-filler` command."""

    root: List[WitnessChunk]


def pytest_addoption(parser: pytest.Parser):
    """Add witness command-line options to pytest."""
    witness_group = parser.getgroup("witness", "Arguments for witness functionality")
    witness_group.addoption(
        "--witness",
        "--witness-the-fitness",
        action="store_true",
        dest="witness",
        default=False,
        help=(
            "Install the witness-filler tool and generate execution witness data for blockchain "
            "test fixtures."
        ),
    )


def pytest_configure(config):
    """
    Pytest hook called after command line options have been parsed.

    If --witness is enabled, installs the witness-filler tool from the specified
    git repository.
    """
    if config.getoption("witness"):
        print("🔧 Installing witness-filler tool from kevaundray/reth...")
        print("   This may take several minutes for first-time compilation...")

        result = subprocess.run(
            [
                "cargo",
                "install",
                "--git",
                "https://github.com/kevaundray/reth.git",
                "--rev",
                "e7efffd314a003018883caf2489c39733fc59388",
                "witness-filler",
            ],
        )

        if result.returncode != 0:
            pytest.exit(
                f"Failed to install witness-filler tool (exit code: {result.returncode}). "
                "Please ensure you have a compatible Rust toolchain installed. "
                "You may need to update your Rust version to 1.86+ or run without --witness.",
                1,
            )
        else:
            print("✅ witness-filler tool installed successfully!")


@pytest.fixture
def witness_generator(request: pytest.FixtureRequest) -> Callable[[Any], None] | None:
    """
    Provide a witness generator function if --witness is enabled.

    Returns:
        None if witness functionality is disabled.
        Callable that generates witness data for a fixture if enabled.

    """
    if not request.config.getoption("witness"):
        return None

    def generate_witness(fixture: Any) -> None:
        """Generate witness data for a fixture using the witness-filler tool."""
        if not hasattr(fixture, "blocks") or not fixture.blocks:
            return

        # Hotfix: witness-filler expects "Merge" but execution-spec-tests uses "Paris"
        original_fork = None
        if hasattr(fixture, "fork") and str(fixture.fork) == "Paris":
            original_fork = fixture.fork
            fixture.fork = "Merge"

        try:
            result = subprocess.run(
                ["witness-filler"],
                input=fixture.model_dump_json(by_alias=True),
                text=True,
                capture_output=True,
            )
        finally:
            # Restore original fork value
            if original_fork is not None:
                fixture.fork = original_fork

        if result.returncode != 0:
            raise RuntimeError(
                f"witness-filler tool failed with exit code {result.returncode}. "
                f"stderr: {result.stderr}"
            )

        try:
            result_model = WitnessFillerResult.model_validate_json(result.stdout)
            witnesses = result_model.root

            for i, witness in enumerate(witnesses):
                if i < len(fixture.blocks) and isinstance(fixture.blocks[i], FixtureBlock):
                    fixture.blocks[i].execution_witness = witness
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse witness data from witness-filler tool. "
                f"Output was: {result.stdout[:500]}{'...' if len(result.stdout) > 500 else ''}"
            ) from e

    return generate_witness
