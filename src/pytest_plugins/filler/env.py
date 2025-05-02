import pytest

from ethereum_test_types.types import DEFAULT_BLOCK_GAS_LIMIT, Environment


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command line options for pytest."""
    env_group = parser.getgroup("env", "Arguments defining the environment")
    env_group.addoption(
        "--block-gas-limit",
        action="store",
        dest="block_gas_limit",
        default=DEFAULT_BLOCK_GAS_LIMIT,
        type=int,
        help=(f"Maximum gas used for blocks. (Default: {DEFAULT_BLOCK_GAS_LIMIT})"),
    )


@pytest.fixture(scope="function")
def env(request: pytest.FixtureRequest) -> Environment:
    """Set the environment for the test."""
    return Environment(
        block_gas_limit=request.config.getoption("block_gas_limit", DEFAULT_BLOCK_GAS_LIMIT)
    )
