"""Defines EIP-7907 specification constants and functions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7907 = ReferenceSpec("EIPS/eip-7907.md", "d758026fc3bd5ac21b652e73d244dee803b1fe44")


@dataclass(frozen=True)
class Spec:
    """
    Reference constants from EIP-7907 specification.

    Note: Tests should use fork methods for actual values, not these constants directly.
    """

    MAX_CODE_SIZE = 0x40000
    MAX_INIT_CODE_SIZE = 0x80000
    LARGE_CONTRACT_THRESHOLD = 0x6000
    GAS_INIT_CODE_WORD_COST = 2
