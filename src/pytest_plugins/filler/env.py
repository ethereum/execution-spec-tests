import pytest

from ethereum_test_types.types import DEFAULT_BLOCK_GAS_LIMIT, Environment


@pytest.fixture(scope="function")
def env(request: pytest.FixtureRequest) -> Environment:
    """Set the environment for the test."""
    return Environment(
        block_gas_limit=request.config.getoption("block_gas_limit", DEFAULT_BLOCK_GAS_LIMIT)
    )
