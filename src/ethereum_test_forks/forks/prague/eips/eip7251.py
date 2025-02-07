"""EIP-7251: Increase the `MAX_EFFECTIVE_BALANCE`."""

from typing import List, Mapping

from ethereum_test_base_types import Address
from ethereum_test_forks.base_eip import EIP, BaseEIP
from ethereum_test_forks.eips import EIP7685


class EIP7251(BaseEIP, fork="Prague"):
    """
    EIP-7251: Increase the `MAX_EFFECTIVE_BALANCE`.

    Allow validators to have larger effective balances, while maintaining the 32 ETH lower bound.
    """

    CONSOLIDATION_REQUEST_CONTRACT_ADDRESS = Address(0x0000BBDDC7CE488642FB579F8B00F3A590007251)
    CONSOLIDATION_REQUEST_TYPE = b"2"

    @classmethod
    def system_contracts(cls) -> List[Address]:
        """Return the consolidation request contract address."""
        return [cls.CONSOLIDATION_REQUEST_CONTRACT_ADDRESS]

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Pre-allocate the consolidation request contract."""
        with open(".contracts" / "consolidation_request.bin", mode="rb") as f:
            return {
                cls.CONSOLIDATION_REQUEST_CONTRACT_ADDRESS: {
                    "nonce": 1,
                    "code": f.read(),
                }
            }

    def required_eips() -> List[EIP]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        return [
            EIP7685,  # Beacon chain request hash bus
        ]
