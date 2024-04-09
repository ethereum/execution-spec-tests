"""
Defines EIP-2537 specification constants and functions.
"""
from dataclasses import dataclass
from typing import Callable

from ethereum_test_forks import Prague


@dataclass(frozen=True)
class ReferenceSpec:
    """
    Defines the reference spec version and git path.
    """

    git_path: str
    version: str


ref_spec_2537 = ReferenceSpec("EIPS/eip-2537.md", "2bba479052f7901c1a981df09ba60cc409e0f3eb")

FORK = Prague


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-2537 specifications as defined at
    https://eips.ethereum.org/EIPS/eip-2537
    """

    # Addresses
    BLS12_G1ADD = 0x0B
    BLS12_G1MUL = 0x0C
    BLS12_G1MSM = 0x0D
    BLS12_G2ADD = 0x0E
    BLS12_G2MUL = 0x0F
    BLS12_G2MSM = 0x10
    BLS12_PAIRING = 0x11
    BLS12_MAP_FP_TO_G1 = 0x12
    BLS12_MAP_FP2_TO_G2 = 0x13

    # Gas constants
    BLS12_G1ADD_GAS = 500
    BLS12_G1MUL_GAS = 12_000
    BLS12_G2ADD_GAS = 800
    BLS12_G2MUL_GAS = 45_000
    BLS12_MAP_FP_TO_G1_GAS = 5_500
    BLS12_MAP_FP2_TO_G2_GAS = 75_000

    # Other constants
    BLS12_LEN_PER_PAIR = 384
    BLS12_MSM_MULTIPLIER = 1_000
    BLS12_MSM_DISCOUNT_TABLE = [
        0,
        1200,
        888,
        764,
        641,
        594,
        547,
        500,
        453,
        438,
        423,
        408,
        394,
        379,
        364,
        349,
        334,
        330,
        326,
        322,
        318,
        314,
        310,
        306,
        302,
        298,
        294,
        289,
        285,
        281,
        277,
        273,
        269,
        268,
        266,
        265,
        263,
        262,
        260,
        259,
        257,
        256,
        254,
        253,
        251,
        250,
        248,
        247,
        245,
        244,
        242,
        241,
        239,
        238,
        236,
        235,
        233,
        232,
        231,
        229,
        228,
        226,
        225,
        223,
        222,
        221,
        220,
        219,
        219,
        218,
        217,
        216,
        216,
        215,
        214,
        213,
        213,
        212,
        211,
        211,
        210,
        209,
        208,
        208,
        207,
        206,
        205,
        205,
        204,
        203,
        202,
        202,
        201,
        200,
        199,
        199,
        198,
        197,
        196,
        196,
        195,
        194,
        193,
        193,
        192,
        191,
        191,
        190,
        189,
        188,
        188,
        187,
        186,
        185,
        185,
        184,
        183,
        182,
        182,
        181,
        180,
        179,
        179,
        178,
        177,
        176,
        176,
        175,
        174,
    ]

    BLS12_MSM_MAX_DISCOUNT = 174


assert Spec.BLS12_MSM_MAX_DISCOUNT == Spec.BLS12_MSM_DISCOUNT_TABLE[-1]


def g1_addition_format(x: int, y: int) -> bytes:
    """
    Formats the input for the BLS12_G1ADD precompile.
    """
    return x.to_bytes(128, byteorder="big") + y.to_bytes(128, byteorder="big")


def g1_multiplication_format(x: int, s: int) -> bytes:
    """
    Formats the input for the BLS12_G1MUL precompile.
    """
    return x.to_bytes(128, byteorder="big") + s.to_bytes(32, byteorder="big")


def g1_multi_scalar_multiplication_format(*args: int) -> bytes:
    """
    Formats the input for the BLS12_G1MSM precompile.
    """
    return b"".join(
        x.to_bytes(128 if i % 2 == 0 else 32, byteorder="big") for i, x in enumerate(args)
    )


def g2_addition_format(x: int, y: int) -> bytes:
    """
    Formats the input for the BLS12_G2ADD precompile.
    """
    return x.to_bytes(256, byteorder="big") + y.to_bytes(256, byteorder="big")


def g2_multiplication_format(x: int, s: int) -> bytes:
    """
    Formats the input for the BLS12_G2MUL precompile.
    """
    return x.to_bytes(256, byteorder="big") + s.to_bytes(32, byteorder="big")


def g2_multi_scalar_multiplication_format(*args: int) -> bytes:
    """
    Formats the input for the BLS12_G2MSM precompile.
    """
    return b"".join(
        x.to_bytes(256 if i % 2 == 0 else 32, byteorder="big") for i, x in enumerate(args)
    )


def pairing_format(*args: int) -> bytes:
    """
    Formats the input for the BLS12_PAIRING precompile.
    """
    return b"".join(
        x.to_bytes(128 if i % 2 == 0 else 256, byteorder="big") for i, x in enumerate(args)
    )


def map_fp_to_g1_format(x: int) -> bytes:
    """
    Formats the input for the BLS12_MAP_FP_TO_G1 precompile.
    """
    return x.to_bytes(64, byteorder="big")


def map_fp2_to_g2_format(x: int) -> bytes:
    """
    Formats the input for the BLS12_MAP_FP2_TO_G2 precompile.
    """
    return x.to_bytes(128, byteorder="big")


def bls12_msm_discount(k: int) -> int:
    """
    Returns the discount for the BLS12_G1MSM and BLS12_G2MSM precompiles.
    """
    return Spec.BLS12_MSM_DISCOUNT_TABLE[min(k, 128)]


def bls12_msm_gas_func_gen(len_per_pair: int, multiplication_cost: int) -> Callable[[int], int]:
    """
    Generates a function that calculates the gas cost for the BLS12_G1MSM and BLS12_G2MSM
    precompiles.
    """

    def bls12_msm_gas(input_length: int) -> int:
        """
        Calculates the gas cost for the BLS12_G1MSM and BLS12_G2MSM precompiles.
        """
        k = input_length // len_per_pair
        if k == 0:
            return 0

        gas_cost = k * multiplication_cost * bls12_msm_discount(k) // Spec.BLS12_MSM_MULTIPLIER

        return gas_cost

    return bls12_msm_gas


g1_multi_scalar_multiplication_gas = bls12_msm_gas_func_gen(160, Spec.BLS12_G1MUL_GAS)
g2_multi_scalar_multiplication_gas = bls12_msm_gas_func_gen(288, Spec.BLS12_G2MUL_GAS)


def bls12_pairing_gas(input_length: int) -> int:
    """
    Calculates the gas cost for the BLS12_PAIRING precompile.
    """
    k = input_length // Spec.BLS12_LEN_PER_PAIR
    return (23000 * k) + 115000
