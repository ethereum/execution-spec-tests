"""Defines EIP-7212 specification constants and functions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7212 = ReferenceSpec("EIPS/eip-7212.md", "06aadd458ee04ede80498db55927b052eb5bef38")


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-7212 specifications as defined at
    https://eips.ethereum.org/EIPS/eip-7212.
    """

    # Address
    P256VERIFY = 0x100

    # Gas constants
    P256VERIFY_GAS = 3450
