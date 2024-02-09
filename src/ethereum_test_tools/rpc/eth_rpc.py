"""
Ethereum `eth_X` JSON-RPC methods used within EEST based hive simulators.
"""

from typing import Dict, List, Literal, Union

from ..common import Address
from .base_rpc import BaseRPC

BlockNumberType = Union[int, Literal["latest", "earliest", "pending"]]


class EthRPC(BaseRPC):
    """
    Represents an `eth_X` RPC class for every default ethereum RPC method used within EEST based
    hive simulators.
    """

    def get_block_by_number(self, block_number: BlockNumberType = "latest", full_txs: bool = True):
        """
        `eth_getBlockByNumber`: Returns information about a block by block number.
        """
        block = hex(block_number) if isinstance(block_number, int) else block_number
        return self.post_request("eth_getBlockByNumber", [block, full_txs])

    def get_balance(self, address: str, block_number: BlockNumberType = "latest"):
        """
        `eth_getBalance`: Returns the balance of the account of given address.
        """
        block = hex(block_number) if isinstance(block_number, int) else block_number
        return self.post_request("eth_getBalance", [address, block])

    def get_transaction_count(self, address: Address, block_number: BlockNumberType = "latest"):
        """
        `eth_getTransactionCount`: Returns the number of transactions sent from an address.
        """
        block = hex(block_number) if isinstance(block_number, int) else block_number
        return self.post_request("eth_getTransactionCount", [address, block])

    def get_storage_at(
        self, address: str, position: str, block_number: BlockNumberType = "latest"
    ):
        """
        `eth_getStorageAt`: Returns the value from a storage position at a given address.
        """
        block = hex(block_number) if isinstance(block_number, int) else block_number
        return self.post_request("eth_getStorageAt", [address, position, block])

    def storage_at_keys(
        self, account: str, keys: List[str], block_number: BlockNumberType = "latest"
    ) -> Dict:
        """
        Helper to retrieve the storage values for the specified keys at a given address and block
        number.
        """
        if isinstance(block_number, int):
            block_number
        results: Dict = {}
        for key in keys:
            storage_value = self.get_storage_at(account, key, block_number)
            results[key] = storage_value
        return results
