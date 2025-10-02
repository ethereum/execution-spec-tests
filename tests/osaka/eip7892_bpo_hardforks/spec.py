"""Defines EIP-7892 specification constants and functions."""

from dataclasses import dataclass

from ethereum_test_forks import Fork


@dataclass(frozen=True)
class ReferenceSpec:
    """Defines the reference spec version and git path."""

    git_path: str
    version: str


ref_spec_7892 = ReferenceSpec("EIPS/eip-7892.md", "a866d892fbf03c80e079ac9f3e58d59bb0f6b1a9")


@dataclass(frozen=True)
class Spec:
    """
    Parameters from the EIP-7892 specifications.

    BPO (Blob Parameter Only) hardforks allow changing only blob-related parameters:
    * target: Expected number of blobs per block
    * max: Maximum number of blobs per block
    * baseFeeUpdateFraction: Blob gas pricing adjustment (accessed via fork methods)
    """

    # Constants from EIP-4844 that remain unchanged in BPO forks
    BLOB_TX_TYPE = 0x03
    FIELD_ELEMENTS_PER_BLOB = 4096
    BLS_MODULUS = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001
    BLOB_COMMITMENT_VERSION_KZG = 0x01
    POINT_EVALUATION_PRECOMPILE_ADDRESS = 0x0A
    POINT_EVALUATION_PRECOMPILE_GAS = 50_000
    GAS_PER_BLOB = 2**17

    @classmethod
    def target_blob_gas_per_block(cls, fork: Fork, timestamp: int = 0) -> int:
        """Get target blob gas per block from fork parameters."""
        return fork.target_blobs_per_block(timestamp=timestamp) * fork.blob_gas_per_blob(
            timestamp=timestamp
        )

    @classmethod
    def max_blob_gas_per_block(cls, fork: Fork, timestamp: int = 0) -> int:
        """Get max blob gas per block from fork parameters."""
        return fork.max_blobs_per_block(timestamp=timestamp) * fork.blob_gas_per_blob(
            timestamp=timestamp
        )

    @classmethod
    def get_blob_base_fee_update_fraction(cls, fork: Fork, timestamp: int = 0) -> int:
        """Get the blob base fee update fraction for the given fork and timestamp."""
        return fork.blob_base_fee_update_fraction(timestamp=timestamp)

    @classmethod
    def verify_bpo_fork_parameters(
        cls,
        fork: Fork,
        pre_fork_timestamp: int,
        post_fork_timestamp: int,
    ) -> dict:
        """
        Verify that only blob parameters changed across a BPO fork boundary.
        Returns a dict of parameter changes.
        """
        changes = {}

        # Check target blobs
        pre_target = fork.target_blobs_per_block(timestamp=pre_fork_timestamp)
        post_target = fork.target_blobs_per_block(timestamp=post_fork_timestamp)
        if pre_target != post_target:
            changes["target_blobs"] = (pre_target, post_target)

        # Check max blobs
        pre_max = fork.max_blobs_per_block(timestamp=pre_fork_timestamp)
        post_max = fork.max_blobs_per_block(timestamp=post_fork_timestamp)
        if pre_max != post_max:
            changes["max_blobs"] = (pre_max, post_max)

        # Check base fee update fraction
        pre_fraction = fork.blob_base_fee_update_fraction(timestamp=pre_fork_timestamp)
        post_fraction = fork.blob_base_fee_update_fraction(timestamp=post_fork_timestamp)
        if pre_fraction != post_fraction:
            changes["base_fee_update_fraction"] = (pre_fraction, post_fraction)

        return changes
