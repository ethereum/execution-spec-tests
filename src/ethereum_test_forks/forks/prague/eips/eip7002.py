"""EIP-7002 definition."""

from typing import List, Mapping

from ethereum_test_base_types import Address

from ....base_eip import EIP, BaseEIP
from .eip7685 import EIP7685


class EIP7002(BaseEIP, fork="Prague"):
    """
    EIP-7002: Withdrawal request contract implementation.

    Allow validators to trigger exits and partial withdrawals via their execution layer (0x01)
    withdrawal credentials.
    """

    WITHDRAWAL_REQUEST_CONTRACT_ADDRESS = Address(0x00000961EF480EB55E80D19AD83579A64C007002)
    WITHDRAWAL_REQUEST_TYPE = b"1"

    @classmethod
    def system_contracts(cls) -> List[Address]:
        """Return the withdrawal request contract address."""
        return [cls.WITHDRAWAL_REQUEST_CONTRACT_ADDRESS]

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Pre-allocate the withdrawal request contract."""
        with open(".contracts" / "withdrawal_request.bin", mode="rb") as f:
            return {
                cls.WITHDRAWAL_REQUEST_CONTRACT_ADDRESS: {
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
