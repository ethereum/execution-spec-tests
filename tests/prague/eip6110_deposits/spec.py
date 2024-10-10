"""
Defines EIP-6110 specification constants and functions.
"""
from dataclasses import dataclass

from ethereum_test_addresses import SystemContract


@dataclass(frozen=True)
class ReferenceSpec:
    """
    Defines the reference spec version and git path.
    """

    git_path: str
    version: str


ref_spec_6110 = ReferenceSpec("EIPS/eip-6110.md", "70a6ec21f62937caf665d98db2b41633e9287871")


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-6110 specifications as defined at
    https://eips.ethereum.org/EIPS/eip-6110
    """

    DEPOSIT_CONTRACT_ADDRESS = SystemContract.BEACON_DEPOSITS
