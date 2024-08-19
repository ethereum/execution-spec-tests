"""
Chain definition for the Optimism network.
"""
from typing import List

import pytest

from ethereum_test_forks import Cancun, get_fork_registry, update_fork_registry


class OptimismCancun(Cancun):
    """
    Defines the Optimism Cancun fork, which adds the secp256r1 precompile.
    """

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """
        Optimism added the secp256r1 precompile to its Cancun fork.
        """
        return [0x100] + super(OptimismCancun, cls).precompiles(block_number, timestamp)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    ethereum_mainnet_forks = get_fork_registry()["ethereum-mainnet"]
    assert "Cancun" in ethereum_mainnet_forks, "Cancun fork not found in ethereum-mainnet forks."
    optimism_mainnet_forks = ethereum_mainnet_forks.copy()
    optimism_mainnet_forks["Cancun"] = OptimismCancun
    update_fork_registry("optimism", optimism_mainnet_forks)
