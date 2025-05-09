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

    TEST_VECTOR_PARAMS = [
        ("modexp_nagydani_1_square", 32, 32, 1, 2, 500),
        ("modexp_nagydani_1_qube", 32, 32, 1, 3, 500),
        ("modexp_nagydani_1_pow0x10001", 32, 32, 3, 0x10001, 682),
        ("modexp_nagydani_2_square", 64, 64, 1, 2, 500),
        ("modexp_nagydani_2_qube", 64, 64, 1, 3, 500),
        ("modexp_nagydani_2_pow0x10001", 64, 64, 3, 0x10001, 2730),
        ("modexp_nagydani_3_square", 96, 96, 1, 2, 682),
        ("modexp_nagydani_3_qube", 96, 96, 1, 3, 682),
        ("modexp_nagydani_3_pow0x10001", 96, 96, 3, 0x10001, 10922),
        ("modexp_nagydani_4_square", 128, 128, 1, 2, 2730),
        ("modexp_nagydani_4_qube", 128, 128, 1, 3, 2730),
        ("modexp_nagydani_4_pow0x10001", 128, 128, 3, 0x10001, 43690),
        ("modexp_nagydani_5_square", 160, 160, 1, 2, 10922),
        ("modexp_nagydani_5_qube", 160, 160, 1, 3, 10922),
        ("modexp_nagydani_5_pow0x10001", 160, 160, 3, 0x10001, 174762),
        ("modexp_marius_1_even", 64, 64, 2, 0xFFFF, 3774),
        ("modexp_guido_1_even", 64, 64, 2, 0x10001, 4261),
        ("modexp_guido_2_even", 64, 64, 2, 0x10001, 4262),
        ("modexp_guido_3_even", 96, 96, 2, 0x10001, 10800),
        ("modexp_guido_4_even", 64, 64, 2, 0x10001, 1967),
        ("modexp_marcin_1_base_heavy", 96, 96, 1, 2, 500),
        ("modexp_marcin_1_exp_heavy", 32, 32, 20, 0x10001, 500),
        ("modexp_marcin_1_balanced", 64, 64, 10, 0x10001, 500),
        ("modexp_marcin_2_base_heavy", 128, 128, 1, 2, 1734),
        ("modexp_marcin_2_exp_heavy", 64, 64, 20, 0x10001, 1364),
        ("modexp_marcin_2_balanced", 96, 96, 10, 0x10001, 1992),
        ("modexp_marcin_3_base_heavy", 160, 160, 1, 2, 677),
        ("modexp_marcin_3_exp_heavy", 96, 96, 20, 0x10001, 765),
        ("modexp_marcin_3_balanced", 128, 128, 10, 0x10001, 1360),
    ]

    OLD_TEST_VECTOR_PARAMS = [
        ("modexp_nagydani_1_square", 32, 32, 1, 2, 200),
        ("modexp_nagydani_1_qube", 32, 32, 1, 3, 200),
        ("modexp_nagydani_1_pow0x10001", 32, 32, 3, 0x10001, 341),
        ("modexp_nagydani_2_square", 64, 64, 1, 2, 200),
        ("modexp_nagydani_2_qube", 64, 64, 1, 3, 200),
        ("modexp_nagydani_2_pow0x10001", 64, 64, 3, 0x10001, 1365),
        ("modexp_nagydani_3_square", 96, 96, 1, 2, 341),
        ("modexp_nagydani_3_qube", 96, 96, 1, 3, 341),
        ("modexp_nagydani_3_pow0x10001", 96, 96, 3, 0x10001, 5461),
        ("modexp_nagydani_4_square", 128, 128, 1, 2, 1365),
        ("modexp_nagydani_4_qube", 128, 128, 1, 3, 1365),
        ("modexp_nagydani_4_pow0x10001", 128, 128, 3, 0x10001, 21845),
        ("modexp_nagydani_5_square", 160, 160, 1, 2, 5461),
        ("modexp_nagydani_5_qube", 160, 160, 1, 3, 5461),
        ("modexp_nagydani_5_pow0x10001", 160, 160, 3, 0x10001, 87381),
        ("modexp_marius_1_even", 64, 64, 2, 0xFFFF, 2057),
        ("modexp_guido_1_even", 64, 64, 2, 0x10001, 2298),
        ("modexp_guido_2_even", 64, 64, 2, 0x10001, 2300),
        ("modexp_guido_3_even", 96, 96, 2, 0x10001, 5400),
        ("modexp_guido_4_even", 64, 64, 2, 0x10001, 1026),
        ("modexp_marcin_1_base_heavy", 96, 96, 1, 2, 200),
        ("modexp_marcin_1_exp_heavy", 32, 32, 20, 0x10001, 215),
        ("modexp_marcin_1_balanced", 64, 64, 10, 0x10001, 200),
        ("modexp_marcin_2_base_heavy", 128, 128, 1, 2, 867),
        ("modexp_marcin_2_exp_heavy", 64, 64, 20, 0x10001, 852),
        ("modexp_marcin_2_balanced", 96, 96, 10, 0x10001, 996),
        ("modexp_marcin_3_base_heavy", 160, 160, 1, 2, 677),
        ("modexp_marcin_3_exp_heavy", 96, 96, 20, 0x10001, 765),
        ("modexp_marcin_3_balanced", 128, 128, 10, 0x10001, 1360),
    ]

    @staticmethod
    def _calculate_modexp_gas_cost(
        base_length: int,
        modulus_length: int,
        exponent_length: int,
        exponent: int,
        exponent_byte_multiplier: int,
        min_gas: int,
        base_modulus_threshold: int = None,
        large_base_multiplier: int = None,
    ) -> int:
        """Calculate Modexp gas cost based on inputs."""
        max_length = max(base_length, modulus_length)
        words = math.ceil(max_length / Spec.WORD_SIZE)

        if base_modulus_threshold is not None and max_length > base_modulus_threshold:
            multiplication_complexity = large_base_multiplier * (words**2)
        else:
            multiplication_complexity = words**2

        if exponent_length <= Spec.EXPONENT_THRESHOLD:
            base_iters = 0 if exponent == 0 else (exponent.bit_length() - 1)
            iteration_count = (exponent_byte_multiplier // 2) * base_iters
        else:
            high_bytes = exponent_length - Spec.EXPONENT_THRESHOLD
            low_bits = (exponent & (2**256 - 1)).bit_length() - 1
            iteration_count = exponent_byte_multiplier * high_bytes + low_bits
        iteration_count = max(iteration_count, 1)

        gas_cost = (multiplication_complexity * iteration_count) // Spec.GAS_DIVISOR
        return max(min_gas, gas_cost)

    @staticmethod
    def calculate_old_gas_cost(
        base_length: int, modulus_length: int, exponent_length: int, exponent: int
    ) -> int:
        """Calculate the ModExp gas cost according to EIP-2565."""
        return Spec._calculate_modexp_gas_cost(
            base_length,
            modulus_length,
            exponent_length,
            exponent,
            exponent_byte_multiplier=Spec.OLD_EXPONENT_BYTE_MULTIPLIER,
            min_gas=Spec.OLD_MIN_GAS,
        )

    @staticmethod
    def calculate_new_gas_cost(
        base_length: int, modulus_length: int, exponent_length: int, exponent: int
    ) -> int:
        """Calculate the ModExp gas cost according to EIP-7883."""
        return Spec._calculate_modexp_gas_cost(
            base_length,
            modulus_length,
            exponent_length,
            exponent,
            exponent_byte_multiplier=Spec.NEW_EXPONENT_BYTE_MULTIPLIER,
            min_gas=Spec.NEW_MIN_GAS,
            base_modulus_threshold=Spec.BASE_MODULUS_THRESHOLD,
            large_base_multiplier=Spec.NEW_LARGE_BASE_MODULUS_MULTIPLIER,
        )

    @staticmethod
    def create_modexp_input(base: bytes, exponent: bytes, modulus: bytes) -> bytes:
        """Format input for the ModExp precompile."""
        base_len = len(base).to_bytes(32, byteorder="big")
        exponent_len = len(exponent).to_bytes(32, byteorder="big")
        modulus_len = len(modulus).to_bytes(32, byteorder="big")
        return base_len + exponent_len + modulus_len + base + exponent + modulus
