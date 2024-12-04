"""
Defines EIP-7742 specification constants and helper functions.
"""

from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from ethereum_test_tools import Transaction


@dataclass(frozen=True)
class BlockHeaderBlobGasFields:
    """
    A helper class for the blob gas fields in a block header.
    """

    excess_blob_gas: int
    blob_gas_used: int


@dataclass(frozen=True)
class ReferenceSpec:
    """
    Defines the reference spec version and git path.
    """

    git_path: str
    version: str


ref_spec_7742 = ReferenceSpec("EIPS/eip-7742.md", "54820d0d83b2369ac957bec6ee7deaeba1c1e4bb")


@dataclass(frozen=True)
class Spec:
    """
    Parameters used for testing EIP-7742 defined at:
    https://eips.ethereum.org/EIPS/eip-7742#parameters

    Some parameters come from the default EIP-4844 specifications as EIP-7742
    is an extension of EIP-4844.
    """

    # EIP-4844 parameters
    BLOB_TX_TYPE = 0x03
    FIELD_ELEMENTS_PER_BLOB = 4096
    BLS_MODULUS = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001
    BLOB_COMMITMENT_VERSION_KZG = 1
    POINT_EVALUATION_PRECOMPILE_ADDRESS = 10
    POINT_EVALUATION_PRECOMPILE_GAS = 50_000
    CANCUN_MAX_BLOB_GAS_PER_BLOCK = 786432
    CANCUN_TARGET_BLOB_GAS_PER_BLOCK = 393216
    MIN_BLOB_GASPRICE = 1
    BLOB_GASPRICE_UPDATE_FRACTION = 3338477
    GAS_PER_BLOB = 2**17
    HASH_OPCODE_BYTE = 0x49
    HASH_GAS_COST = 3

    # EIP-7742 parameters
    CANCUN_MAX_BLOBS_PER_BLOCK = 6
    CANCUN_TARGET_BLOBS_PER_BLOCK = 3

    @classmethod
    def kzg_to_versioned_hash(
        cls,
        kzg_commitment: bytes | int,  # 48 bytes
        blob_commitment_version_kzg: Optional[bytes | int] = None,
    ) -> bytes:
        """
        Calculates the versioned hash for a given KZG commitment.
        """
        if blob_commitment_version_kzg is None:
            blob_commitment_version_kzg = cls.BLOB_COMMITMENT_VERSION_KZG
        if isinstance(kzg_commitment, int):
            kzg_commitment = kzg_commitment.to_bytes(48, "big")
        if isinstance(blob_commitment_version_kzg, int):
            blob_commitment_version_kzg = blob_commitment_version_kzg.to_bytes(1, "big")
        return blob_commitment_version_kzg + sha256(kzg_commitment).digest()[1:]

    @classmethod
    def fake_exponential(cls, factor: int, numerator: int, denominator: int) -> int:
        """
        Used to calculate the blob gas cost.
        """
        i = 1
        output = 0
        numerator_accumulator = factor * denominator
        while numerator_accumulator > 0:
            output += numerator_accumulator
            numerator_accumulator = (numerator_accumulator * numerator) // (denominator * i)
            i += 1
        return output // denominator

    @classmethod
    def calc_excess_blob_gas(cls, parent: BlockHeaderBlobGasFields) -> int:
        """
        Calculate the excess blob gas for a block given the excess blob gas
        and blob gas used from the parent block header.
        """
        if parent.excess_blob_gas + parent.blob_gas_used < cls.CANCUN_TARGET_BLOB_GAS_PER_BLOCK:
            return 0
        else:
            return (
                parent.excess_blob_gas
                + parent.blob_gas_used
                - cls.CANCUN_TARGET_BLOB_GAS_PER_BLOCK
            )

    @classmethod
    def get_total_blob_gas(cls, tx: Transaction) -> int:
        """
        Calculate the total blob gas for a transaction.
        """
        if tx.blob_versioned_hashes is None:
            return 0
        return cls.GAS_PER_BLOB * len(tx.blob_versioned_hashes)

    @classmethod
    def get_blob_gasprice(cls, *, excess_blob_gas: int) -> int:
        """
        Calculate the blob gas price from the excess.
        """
        return cls.fake_exponential(
            cls.MIN_BLOB_GASPRICE,
            excess_blob_gas,
            cls.BLOB_GASPRICE_UPDATE_FRACTION,
        )


class SpecHelpers:
    """
    Define parameters and helper functions that are tightly coupled to the 4844
    spec but not strictly part of it.
    """

    @classmethod
    def calc_excess_blob_gas_from_blob_count(
        cls, parent_excess_blob_gas: int, parent_blob_count: int
    ) -> int:
        """
        Calculate the excess blob gas for a block given the parent excess blob gas
        and the number of blobs in the block.
        """
        parent_consumed_blob_gas = parent_blob_count * Spec.GAS_PER_BLOB
        return Spec.calc_excess_blob_gas(
            BlockHeaderBlobGasFields(parent_excess_blob_gas, parent_consumed_blob_gas)
        )
