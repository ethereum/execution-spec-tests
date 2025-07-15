"""Pytest configuration for all tests."""

import pytest

from ethereum_test_tools import Environment
from pytest_plugins.filler.filler import FillMode

GIGA_GAS = 1_000_000_000


@pytest.fixture
def env(request: pytest.FixtureRequest) -> Environment:  # noqa: D103
    """Return an Environment instance with appropriate gas limit based on fill mode."""
    if request.config.fill_mode == FillMode.BENCHMARKING:  # type: ignore[attr-defined]
        return Environment(gas_limit=GIGA_GAS)
    else:
        return Environment()
