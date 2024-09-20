"""
Ethereum test execution base types.
"""
from abc import abstractmethod

from ethereum_test_base_types import CamelModel
from ethereum_test_rpc import EthRPC


class BaseExecute(CamelModel):
    """
    Represents a base execution format.
    """

    @abstractmethod
    def execute(self, eth_rpc: EthRPC):
        """
        Execute the format.
        """
        pass
