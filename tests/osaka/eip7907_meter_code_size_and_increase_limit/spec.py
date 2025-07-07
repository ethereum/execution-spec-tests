"""Defines EIP-7907 specification constants and functions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7907 = ReferenceSpec("EIPS/eip-7907.md", "e9ec317a203e71d13d67bae76eacc1326cc71768")


@dataclass(frozen=True)
class Spec:
    """Constants and helpers for meter code size and increase limit EIP."""

    TARGET_CODE_SIZE = 0x6000 * 2  # TEMP: Current EIP-ref points to 256 KiB. Target: 48 KiB.
