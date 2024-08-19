"""

"""

import pytest
from ethereum_test_forks.fork_registry import get_fork_registry
from ethereum_test_forks.helpers import get_forks


def pytest_addoption(parser):
    parser.addoption(
        "--chain",
        action="store",
        default="ethereum-mainnet",
        help="Select the EVM chain for testing. Default: ethereum-mainnet.",
    )


@pytest.fixture(scope="session")
def chain(request):
    return request.config.getoption("--chain")


@pytest.fixture(scope="session")
def forks(chain):
    fork_registry = get_fork_registry()
    if chain not in fork_registry:
        raise ValueError(f"No forks found for chain: {chain}")
    return fork_registry[chain].values()


# @pytest.hookimpl(tryfirst=True)
# def pytest_generate_tests(metafunc):
#     if "fork" in metafunc.fixturenames:
#         chain = metafunc.config.getoption("chain")
#         fork_registry = get_fork_registry()
#         if chain in fork_registry:
#             forks = fork_registry[chain]
#             metafunc.parametrize(
#                 "fork", forks.values(), ids=[fork.__name__ for fork in forks.values()]
#             )
