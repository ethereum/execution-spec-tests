"""EIP-2537 definition."""

from typing import List

from ethereum_test_base_types import Address
from ethereum_test_forks.base_eip import BaseEIP


class EIP2537(BaseEIP, fork="Prague"):
    """
    EIP-2537: Precompile for BLS12-381 curve operations.

    Adds operation on BLS12-381 curve as a precompile in a set necessary to efficiently perform
    operations such as BLS signature verification.
    """

    BLS12_G1ADD = Address(0x0B)
    BLS12_G1MSM = Address(0x0C)
    BLS12_G2ADD = Address(0x0D)
    BLS12_G2MSM = Address(0x0E)
    BLS12_PAIRING_CHECK = Address(0x0F)
    BLS12_MAP_FP_TO_G1 = Address(0x10)
    BLS12_MAP_FP2_TO_G2 = Address(0x11)

    @classmethod
    def eip_precompiles(cls) -> List[Address]:
        """Return the BLS operation precompiles (0x0B through 0x11)."""
        return [
            cls.BLS12_G1ADD,
            cls.BLS12_G1MSM,
            cls.BLS12_G2ADD,
            cls.BLS12_G2MSM,
            cls.BLS12_PAIRING_CHECK,
            cls.BLS12_MAP_FP_TO_G1,
            cls.BLS12_MAP_FP2_TO_G2,
        ]
