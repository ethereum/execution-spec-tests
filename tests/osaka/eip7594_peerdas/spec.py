"""Defines EIP-7594 specification constants and functions."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7594 = ReferenceSpec("EIPS/eip-7594.md", "45d03a84a8ad0160ed3fb03af52c49bd39e802ba")


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-7594 specifications as defined at
    https://eips.ethereum.org/EIPS/eip-7594.
    """

    FIELD_ELEMENTS_PER_BLOB = 4096
    BYTES_PER_FIELD_ELEMENT = 32
    BYTES_PER_BLOB = FIELD_ELEMENTS_PER_BLOB * BYTES_PER_FIELD_ELEMENT  # 131072
    CELL_LENGTH = 2048
    BLS_MODULUS = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001  # EIP-2537: Main subgroup order = q  # noqa: E501
    # due to BLS_MODULUS every blob byte (uint256) must be smaller than 116

    # deneb constants that have not changed (https://github.com/ethereum/consensus-specs/blob/cc6996c22692d70e41b7a453d925172ee4b719ad/specs/deneb/polynomial-commitments.md?plain=1#L78)
    BYTES_PER_PROOF = 48
    BYTES_PER_COMMITMENT = 48
    KZG_ENDIANNESS: Literal["big"] = "big"

    # eip-7691
    MAX_BLOBS_PER_BLOCK_ELECTRA = 9
    TARGET_BLOBS_PER_BLOCK_ELECTRA = 6
    MAX_BLOB_GAS_PER_BLOCK = 1179648
    TARGET_BLOB_GAS_PER_BLOCK = 786432
    BLOB_BASE_FEE_UPDATE_FRACTION_PRAGUE = 5007716
