"""Defines EIP-7883 specification constants and functions."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7883 = ReferenceSpec("EIPS/eip-7883.md", "13aa65810336d4f243d4563a828d5afe36035d23")


@dataclass(frozen=True)
class Spec:
    """Constants and helpers for the ModExp gas cost increase EIP."""

    MODEXP_ADDRESS = 0x05
    OLD_MIN_GAS = 200
    OLD_EXPONENT_BYTE_MULTIPLIER = 8
    NEW_MIN_GAS = 500
    NEW_EXPONENT_BYTE_MULTIPLIER = 16
    NEW_LARGE_BASE_MODULUS_MULTIPLIER = 2
    WORD_SIZE = 8
    BASE_MODULUS_THRESHOLD = 32
    EXPONENT_THRESHOLD = 32
    GAS_DIVISOR = 3

    @staticmethod
    def calculate_new_gas_cost(
        base_length: int, modulus_length: int, exponent_length: int, exponent: int
    ) -> int:
        """Calculate the ModExp gas cost according to EIP-7883 specification."""
        max_length = max(base_length, modulus_length)
        words = math.ceil(max_length / Spec.WORD_SIZE)
        if max_length <= Spec.BASE_MODULUS_THRESHOLD:
            multiplication_complexity = words**2
        else:
            multiplication_complexity = 2 * words**2
        if exponent_length <= Spec.EXPONENT_THRESHOLD:
            if exponent == 0:
                iteration_count = 0
            else:
                iteration_count = exponent.bit_length() - 1
        else:
            high_bytes = exponent_length - Spec.EXPONENT_THRESHOLD
            low_bits = (exponent & (2**256 - 1)).bit_length() - 1
            iteration_count = (Spec.NEW_EXPONENT_BYTE_MULTIPLIER * high_bytes) + low_bits
        iteration_count = max(iteration_count, 1)
        gas_cost = (multiplication_complexity * iteration_count) // Spec.GAS_DIVISOR
        return max(Spec.NEW_MIN_GAS, gas_cost)
