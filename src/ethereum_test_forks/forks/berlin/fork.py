"""Berlin fork definition."""

from typing import List, Sized

from ethereum_test_base_types import AccessList
from ethereum_test_base_types.conversions import BytesConvertible
from ethereum_test_forks.base_fork import (
    TransactionIntrinsicCostCalculator,
)
from ethereum_test_forks.forks.istanbul.fork import Istanbul


class Berlin(Istanbul):
    """Berlin fork."""

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At Berlin, access list transactions are introduced."""
        return [1] + super(Berlin, cls).tx_types(block_number, timestamp)

    @classmethod
    def contract_creating_tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At Berlin, access list transactions are introduced."""
        return [1] + super(Berlin, cls).contract_creating_tx_types(block_number, timestamp)

    @classmethod
    def transaction_intrinsic_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionIntrinsicCostCalculator:
        """At Berlin, the transaction intrinsic cost needs to take the access list into account."""
        super_fn = super(Berlin, cls).transaction_intrinsic_cost_calculator(
            block_number, timestamp
        )
        gas_costs = cls.gas_costs(block_number, timestamp)

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
                authorization_list_or_count=authorization_list_or_count,
            )
            if access_list is not None:
                for access in access_list:
                    intrinsic_cost += gas_costs.G_ACCESS_LIST_ADDRESS
                    for _ in access.storage_keys:
                        intrinsic_cost += gas_costs.G_ACCESS_LIST_STORAGE
            return intrinsic_cost

        return fn
