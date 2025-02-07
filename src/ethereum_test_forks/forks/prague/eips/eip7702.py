"""EIP-7702 definition."""

from typing import List

from ethereum_test_forks.base_eip import EIP, BaseEIP


class EIP7702(BaseEIP, fork="Prague"):
    """
    EIP-7702: Set EOA account code.

    Add a new tx type that permanently sets the code for an EOA.
    """

    SET_CODE_TX_TYPE = 0x04
    MAGIC = 0x05
    PER_AUTH_BASE_COST = 12500
    PER_EMPTY_ACCOUNT_COST = 25000

    @classmethod
    def tx_types(cls) -> List[int]:
        """Return list of transaction types introduced by this EIP."""
        return [cls.SET_CODE_TX_TYPE]

    @classmethod
    def required_eips(cls) -> List[EIP]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        # TODO: From the spec: Requires EIP-2, EIP-161, EIP-1052, EIP-2718, EIP-2929,
        # EIP-2930, EIP-3541, EIP-3607, EIP-4844
        return []
