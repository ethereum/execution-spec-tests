"""Prague fork implementation."""

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from typing import List, Mapping, Optional, Sized

from semver import Version

from ethereum_test_base_types import AccessList, Address, Bytes
from ethereum_test_base_types.conversions import BytesConvertible

from ..base_fork import (
    CalldataGasCalculator,
    TransactionDataFloorCostCalculator,
    TransactionIntrinsicCostCalculator,
)
from ..gas_costs import GasCosts
from .cancun import Cancun

CURRENT_FOLDER = Path(__file__).parent


class Prague(Cancun):
    """Prague fork."""

    @classmethod
    def is_deployed(cls) -> bool:
        """Flag that the fork has not been deployed to mainnet."""
        return False

    @classmethod
    def solc_min_version(cls) -> Version:
        """Return minimum version of solc that supports this fork."""
        return Version.parse("1.0.0")  # set a high version; currently unknown

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Add BLS operation precompiles."""
        return [Address(i) for i in range(0xB, 0x11 + 1)] + super().precompiles(
            block_number, timestamp
        )

    @classmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """Update gas costs for EIP-7623."""
        return replace(
            super().gas_costs(block_number, timestamp),
            G_TX_DATA_STANDARD_TOKEN_COST=4,
            G_TX_DATA_FLOOR_TOKEN_COST=10,
            G_AUTHORIZATION=25_000,
            R_AUTHORIZATION_EXISTING_AUTHORITY=12_500,
        )

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Prague introduces the system contracts for EIP-6110, EIP-7002, EIP-7251 and EIP-2935."""
        return [
            Address(
                0x00000000219AB540356CBB839CBE05303D7705FA
            ),  # EIP-6110: Beacon chain deposit contract
            Address(
                0x00000961EF480EB55E80D19AD83579A64C007002
            ),  # EIP-7002: Withdrawal request contract
            Address(
                0x0000BBDDC7CE488642FB579F8B00F3A590007251
            ),  # EIP-7251: Consolidation request contract
            Address(
                0x0000F90827F1C53A10CB7A02335B175320002935
            ),  # EIP-2935: History storage contract
        ] + super().system_contracts(block_number, timestamp)

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """Prague requires pre-allocation of several system contracts."""
        new_allocation = {}

        # EIP-6110: Beacon chain deposit contract
        deposit_contract_tree_depth = 32
        storage = {}
        next_hash = sha256(b"\x00" * 64).digest()
        for i in range(deposit_contract_tree_depth + 2, deposit_contract_tree_depth * 2 + 1):
            storage[i] = next_hash
            next_hash = sha256(next_hash + next_hash).digest()

        with open(CURRENT_FOLDER / "contracts" / "deposit_contract.bin", mode="rb") as f:
            new_allocation[0x00000000219AB540356CBB839CBE05303D7705FA] = {
                "nonce": 1,
                "code": f.read(),
                "storage": storage,
            }

        # EIP-7002: Withdrawal request contract
        with open(CURRENT_FOLDER / "contracts" / "withdrawal_request.bin", mode="rb") as f:
            new_allocation[0x00000961EF480EB55E80D19AD83579A64C007002] = {
                "nonce": 1,
                "code": f.read(),
            }

        # EIP-7251: Consolidation request contract
        with open(CURRENT_FOLDER / "contracts" / "consolidation_request.bin", mode="rb") as f:
            new_allocation[0x0000BBDDC7CE488642FB579F8B00F3A590007251] = {
                "nonce": 1,
                "code": f.read(),
            }

        # EIP-2935: History storage contract
        with open(CURRENT_FOLDER / "contracts" / "history_contract.bin", mode="rb") as f:
            new_allocation[0x0000F90827F1C53A10CB7A02335B175320002935] = {
                "nonce": 1,
                "code": f.read(),
            }

        return new_allocation | super().pre_allocation_blockchain()

    @classmethod
    def calldata_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> CalldataGasCalculator:
        """Return calculator for transaction gas cost based on calldata contents."""
        gas_costs = cls.gas_costs(block_number, timestamp)

        def fn(*, data: BytesConvertible, floor: bool = False) -> int:
            tokens = 0
            for b in Bytes(data):
                if b == 0:
                    tokens += 1
                else:
                    tokens += 4
            if floor:
                return tokens * gas_costs.G_TX_DATA_FLOOR_TOKEN_COST
            return tokens * gas_costs.G_TX_DATA_STANDARD_TOKEN_COST

        return fn

    @classmethod
    def transaction_data_floor_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionDataFloorCostCalculator:
        """Calculate the transaction floor cost due to its calldata."""
        calldata_gas_calculator = cls.calldata_gas_calculator(block_number, timestamp)
        gas_costs = cls.gas_costs(block_number, timestamp)

        def fn(*, data: BytesConvertible) -> int:
            return calldata_gas_calculator(data=data, floor=True) + gas_costs.G_TRANSACTION

        return fn

    @classmethod
    def transaction_intrinsic_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionIntrinsicCostCalculator:
        """Calculate the intrinsic gas cost of a transaction."""
        super_fn = super().transaction_intrinsic_cost_calculator(block_number, timestamp)
        gas_costs = cls.gas_costs(block_number, timestamp)
        transaction_data_floor_cost_calculator = cls.transaction_data_floor_cost_calculator(
            block_number, timestamp
        )

        def fn(
            *,
            calldata: BytesConvertible = b"",
            contract_creation: bool = False,
            access_list: List[AccessList] | None = None,
            authorization_list_or_count: Sized | int | None = None,
            return_cost_deducted_prior_execution: bool = False,
        ) -> int:
            intrinsic_cost: int = super_fn(
                calldata=calldata,
                contract_creation=contract_creation,
                access_list=access_list,
                return_cost_deducted_prior_execution=False,
            )
            if authorization_list_or_count is not None:
                if isinstance(authorization_list_or_count, Sized):
                    authorization_list_or_count = len(authorization_list_or_count)
                intrinsic_cost += authorization_list_or_count * gas_costs.G_AUTHORIZATION

            if return_cost_deducted_prior_execution:
                return intrinsic_cost

            transaction_floor_data_cost = transaction_data_floor_cost_calculator(data=calldata)
            return max(intrinsic_cost, transaction_floor_data_cost)

        return fn

    @classmethod
    def max_request_type(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """At Prague, three request types are introduced, hence the max request type is 2."""
        return 2

    @classmethod
    def blob_base_fee_update_fraction(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the blob base fee update fraction for Prague."""
        return 5007716

    @classmethod
    def target_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Target blob count of 6 for Prague."""
        return 6

    @classmethod
    def max_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Max blob count of 9 for Prague."""
        return 9

    @classmethod
    def header_requests_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """
        Prague requires that the execution layer header contains the beacon chain
        requests hash.
        """
        return True

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """From Prague, new payload calls must use version 4."""
        return 4

    @classmethod
    def engine_forkchoice_updated_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """At Prague, version number of NewPayload and ForkchoiceUpdated diverge."""
        return 3
