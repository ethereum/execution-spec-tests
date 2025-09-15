"""Defines EIP-7823 specification constants and functions."""

from dataclasses import dataclass

from ..eip7883_modexp_gas_increase.spec import Spec, ceiling_division


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7823 = ReferenceSpec("EIPS/eip-7823.md", "c8321494fdfbfda52ad46c3515a7ca5dc86b857c")


@dataclass(frozen=True)
class Spec7823(Spec):
    """
    Constants and helpers for the ModExp gas cost increase EIP.
    These override the original Spec class variables for EIP-7823.
    """

    MODEXP_ADDRESS = 0x05
    MIN_GAS = 500

    LARGE_BASE_MODULUS_MULTIPLIER = 2
    EXPONENT_BYTE_MULTIPLIER = 16
    GAS_DIVISOR = 1

    @classmethod
    def calculate_multiplication_complexity(cls, base_length: int, modulus_length: int) -> int:
        """Calculate the multiplication complexity of the ModExp precompile for EIP-7883."""
        max_length = max(base_length, modulus_length)
        words = ceiling_division(max_length, cls.WORD_SIZE)
        complexity = 16
        if max_length > cls.MAX_LENGTH_THRESHOLD:
            complexity = cls.LARGE_BASE_MODULUS_MULTIPLIER * words**2
        return complexity
