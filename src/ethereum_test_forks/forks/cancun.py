"""Cancun fork implementation."""

from typing import List, Mapping, Optional

from semver import Version

from ethereum_test_base_types import Address, BlobSchedule, ForkBlobSchedule
from ethereum_test_vm import Opcodes

from ..base_fork import BlobGasPriceCalculator, ExcessBlobGasCalculator
from .helpers import fake_exponential
from .shanghai import Shanghai


class Cancun(Shanghai):
    """Cancun fork."""

    @classmethod
    def solc_min_version(cls) -> Version:
        """Return minimum version of solc that supports this fork."""
        return Version.parse("0.8.24")

    @classmethod
    def header_excess_blob_gas_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Excess blob gas is required starting from Cancun."""
        return True

    @classmethod
    def header_blob_gas_used_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Blob gas used is required starting from Cancun."""
        return True

    @classmethod
    def header_beacon_root_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Parent beacon block root is required starting from Cancun."""
        return True

    @classmethod
    def blob_gas_price_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> BlobGasPriceCalculator:
        """Return a callable that calculates the blob gas price at Cancun."""
        min_base_fee_per_blob_gas = cls.min_base_fee_per_blob_gas(block_number, timestamp)
        blob_base_fee_update_fraction = cls.blob_base_fee_update_fraction(block_number, timestamp)

        def fn(*, excess_blob_gas) -> int:
            return fake_exponential(
                min_base_fee_per_blob_gas,
                excess_blob_gas,
                blob_base_fee_update_fraction,
            )

        return fn

    @classmethod
    def excess_blob_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> ExcessBlobGasCalculator:
        """Return a callable that calculates the excess blob gas for a block at Cancun."""
        target_blobs_per_block = cls.target_blobs_per_block(block_number, timestamp)
        blob_gas_per_blob = cls.blob_gas_per_blob(block_number, timestamp)
        target_blob_gas_per_block = target_blobs_per_block * blob_gas_per_blob

        def fn(
            *,
            parent_excess_blob_gas: int | None = None,
            parent_excess_blobs: int | None = None,
            parent_blob_gas_used: int | None = None,
            parent_blob_count: int | None = None,
        ) -> int:
            if parent_excess_blob_gas is None:
                assert parent_excess_blobs is not None, "Parent excess blobs are required"
                parent_excess_blob_gas = parent_excess_blobs * blob_gas_per_blob
            if parent_blob_gas_used is None:
                assert parent_blob_count is not None, "Parent blob count is required"
                parent_blob_gas_used = parent_blob_count * blob_gas_per_blob
            if parent_excess_blob_gas + parent_blob_gas_used < target_blob_gas_per_block:
                return 0
            else:
                return parent_excess_blob_gas + parent_blob_gas_used - target_blob_gas_per_block

        return fn

    @classmethod
    def min_base_fee_per_blob_gas(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the minimum base fee per blob gas for Cancun."""
        return 1

    @classmethod
    def blob_base_fee_update_fraction(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the blob base fee update fraction for Cancun."""
        return 3338477

    @classmethod
    def blob_gas_per_blob(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Blobs are enabled starting from Cancun."""
        return 2**17

    @classmethod
    def supports_blobs(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At Cancun, blobs support is enabled."""
        return True

    @classmethod
    def target_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Blobs are enabled starting from Cancun, with a static target of 3 blobs."""
        return 3

    @classmethod
    def max_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Blobs are enabled starting from Cancun, with a static max of 6 blobs."""
        return 6

    @classmethod
    def blob_schedule(cls, block_number: int = 0, timestamp: int = 0) -> BlobSchedule | None:
        """At Cancun, the fork object runs this routine to get the updated blob schedule."""
        parent_fork = cls.parent()
        assert parent_fork is not None, "Parent fork must be defined"
        blob_schedule = parent_fork.blob_schedule(block_number, timestamp)
        if blob_schedule is None:
            last_blob_schedule = None
            blob_schedule = BlobSchedule()
        else:
            last_blob_schedule = blob_schedule.last()
        current_blob_schedule = ForkBlobSchedule(
            target_blobs_per_block=cls.target_blobs_per_block(block_number, timestamp),
            max_blobs_per_block=cls.max_blobs_per_block(block_number, timestamp),
            base_fee_update_fraction=cls.blob_base_fee_update_fraction(block_number, timestamp),
        )
        if last_blob_schedule is None or last_blob_schedule != current_blob_schedule:
            blob_schedule.append(fork=cls.__name__, schedule=current_blob_schedule)
        return blob_schedule

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At Cancun, blob type transactions are introduced."""
        return [3] + super().tx_types(block_number, timestamp)

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """At Cancun, pre-compile for kzg point evaluation is introduced."""
        return [Address(0xA)] + super().precompiles(block_number, timestamp)

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Cancun introduces the system contract for EIP-4788."""
        return [Address(0x000F3DF6D732807EF1319FB7B8BB8522D0BEAC02)]

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """
        Cancun requires pre-allocation of the beacon root contract for EIP-4788
        on blockchain type tests.
        """
        new_allocation = {
            0x000F3DF6D732807EF1319FB7B8BB8522D0BEAC02: {
                "nonce": 1,
                "code": "0x3373fffffffffffffffffffffffffffffffffffffffe14604d57602036146024575f5f"
                "fd5b5f35801560495762001fff810690815414603c575f5ffd5b62001fff01545f5260205ff35b5f"
                "5ffd5b62001fff42064281555f359062001fff015500",
            }
        }
        return new_allocation | super().pre_allocation_blockchain()

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """From Cancun, new payload calls must use version 3."""
        return 3

    @classmethod
    def engine_new_payload_blob_hashes(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """From Cancun, payloads must have blob hashes."""
        return True

    @classmethod
    def engine_new_payload_beacon_root(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """From Cancun, payloads must have a parent beacon block root."""
        return True

    @classmethod
    def valid_opcodes(cls) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [
            Opcodes.BLOBHASH,
            Opcodes.BLOBBASEFEE,
            Opcodes.TLOAD,
            Opcodes.TSTORE,
            Opcodes.MCOPY,
        ] + super().valid_opcodes()
