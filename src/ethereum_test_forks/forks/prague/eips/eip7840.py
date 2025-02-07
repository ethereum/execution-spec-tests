"""EIP-7840 definition."""

from ethereum_test_forks.base_eip import BaseEIP


class EIP7840(BaseEIP, fork="Prague"):
    """
    EIP-7840: Add blob schedule to EL config files.

    Include a per-fork blob parameters in client configuration files.
    """

    pass
