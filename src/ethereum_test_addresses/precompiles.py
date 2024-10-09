"""
Precompile addresses
"""

from enum import Enum

from ethereum_test_base_types import Address


class Precompile(Address, Enum):
    """
    Enum that lists the addresses of precompiles.
    """

    EC_RECOVER = Address(1, label="ec_recover")
    SHA256 = Address(2, label="sha256")
    RIPEMD_160 = Address(3, label="ripemd160")
    IDENTITY = Address(4, label="identity")
    BIG_INT_MOD_EXP = Address(5, label="big_int_mod_exp")
    ALT_BN_128_ADD = Address(6, label="alt_bn_128_add")
    ALT_BN_128_MUL = Address(7, label="alt_bn_128_mul")
    ALT_BN_128_PAIRING = Address(8, label="alt_bn_128_pairing")
    BLAKE2_F = Address(9, label="blake2_f")
    KZG_POINT_EVALUATION = Address(10, label="kzg_point_evaluation")
    BLS_12_381_G1_ADD = Address(11, label="bls_12_381_g1_add")
    BLS_12_381_G1_MUL = Address(12, label="bls_12_381_g1_mul")
    BLS_12_381_G1_MULTIEXP = Address(13, label="bls_12_381_g1_multiexp")
    BLS_12_381_G2_ADD = Address(14, label="bls_12_381_g2_add")
    BLS_12_381_G2_MUL = Address(15, label="bls_12_381_g2_mul")
    BLS_12_381_G2_MULTIEXP = Address(16, label="bls_12_381_g2_multiexp")
    BLS_12_381_PAIRING = Address(17, label="bls_12_381_pairing")
    BLS_12_381_MAP_FP_TO_G1 = Address(18, label="bls_12_381_map_fp_to_g1")
    BLS_12_381_MAP_FP2_TO_G2 = Address(19, label="bls_12_381_map_fp2_to_g2")
