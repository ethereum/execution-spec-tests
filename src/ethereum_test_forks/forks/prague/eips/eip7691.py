"""EIP-7691 definition."""

from ethereum_test_forks.base_eip import BaseEIP


class EIP7691(BaseEIP, fork="Prague"):
    """
    EIP-7691: Blob Parameters for Prague.

    Increase the number of blobs to reach a new target and max of 6 and 9
    blobs per block respectively.
    """

    MAX_BLOBS_PER_BLOCK_ELECTRA = 9
    TARGET_BLOBS_PER_BLOCK_ELECTRA = 6
    MAX_BLOB_GAS_PER_BLOCK = 1179648
    TARGET_BLOB_GAS_PER_BLOCK = 786432
    BLOB_BASE_FEE_UPDATE_FRACTION_PRAGUE = 5007716

    @classmethod
    def eip_blob_base_fee_update_fraction(cls) -> int:
        """Return the blob base fee update fraction."""
        return cls.BLOB_BASE_FEE_UPDATE_FRACTION_PRAGUE

    @classmethod
    def eip_target_blobs_per_block(cls) -> int:
        """Return the target blob count."""
        return cls.TARGET_BLOBS_PER_BLOCK_ELECTRA

    @classmethod
    def eip_max_blobs_per_block(cls) -> int:
        """Return the max blob count."""
        return cls.MAX_BLOBS_PER_BLOCK_ELECTRA
