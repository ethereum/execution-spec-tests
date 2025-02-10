"""EIP-2935 definition."""

from typing import List, Mapping

from ethereum_test_base_types import Address

from ....base_eip import EIP, BaseEIP
from .eip7685 import EIP7685


class EIP2935(BaseEIP, fork="Prague"):
    """
    EIP-2935: Serve historical block hashes from state.

    Store and serve last 8192 block hashes as storage slots of a system contract to allow for
    stateless execution
    """

    HISTORY_STORAGE_CONTRACT_ADDRESS = Address(0x0000F90827F1C53A10CB7A02335B175320002935)
    BLOCKHASH_SERVE_WINDOW = 256
    HISTORY_SERVE_WINDOW = 8191

    @classmethod
    def system_contracts(cls) -> List[Address]:
        """Return the history storage contract address."""
        return [cls.HISTORY_STORAGE_CONTRACT_ADDRESS]

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Pre-allocate the history storage contract."""
        with open(".contracts" / "history_contract.bin", mode="rb") as f:
            return {
                cls.HISTORY_STORAGE_CONTRACT_ADDRESS: {
                    "nonce": 1,
                    "code": f.read(),
                }
            }

    @classmethod
    def required_eips(cls) -> List[EIP]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        return [
            EIP7685,  # Beacon chain request hash bus
        ]
