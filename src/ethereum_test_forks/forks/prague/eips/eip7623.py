"""EIP-7623 definition."""

from dataclasses import replace
from typing import List, Sized

from ethereum_test_base_types import AccessList, Bytes
from ethereum_test_base_types.conversions import BytesConvertible
from ethereum_test_forks.base_eip import BaseEIP
from ethereum_test_forks.base_fork import (
    CalldataGasCalculator,
    TransactionDataFloorCostCalculator,
    TransactionIntrinsicCostCalculator,
)
from ethereum_test_forks.gas_costs import GasCosts


class EIP7623(BaseEIP, fork="Prague"):
    """
    EIP-7623: Increase calldata cost.

    Increase calldata cost to reduce maximum block size.
    """

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
