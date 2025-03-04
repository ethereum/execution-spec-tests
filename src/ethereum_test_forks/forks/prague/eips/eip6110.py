"""EIP-6110 definition."""

from hashlib import sha256
from typing import List, Mapping

from ethereum_test_base_types import Address

from ....base_eip import EIP, BaseEIP
from .eip7685 import EIP7685


class EIP6110(BaseEIP, fork="Prague"):
    """
    EIP-6110: Beacon chain deposit contract.

    Provides validator deposits as a list of deposit operations added to the Execution Layer block.
    """

    DEPOSIT_REQUEST_CONTRACT_ADDRESS = Address(0x00000000219AB540356CBB839CBE05303D7705FA)
    DEPOSIT_REQUEST_TYPE = b"0"

    @classmethod
    def system_contracts(cls) -> List[Address]:
        """Return the beacon chain deposit contract address."""
        return [cls.DEPOSIT_REQUEST_CONTRACT_ADDRESS]

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Pre-allocate the beacon chain deposit contract."""
        deposit_contract_tree_depth = 32
        storage = {}
        next_hash = sha256(b"\x00" * 64).digest()
        for i in range(deposit_contract_tree_depth + 2, deposit_contract_tree_depth * 2 + 1):
            storage[i] = next_hash
            next_hash = sha256(next_hash + next_hash).digest()

        with open(".contracts" / "deposit_contract.bin", mode="rb") as f:
            return {
                cls.DEPOSIT_REQUEST_CONTRACT_ADDRESS: {
                    "nonce": 1,
                    "code": f.read(),
                    "storage": storage,
                }
            }

    @classmethod
    def required_eips(cls) -> List[EIP]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        return [
            EIP7685,  # Beacon chain request hash bus
        ]
