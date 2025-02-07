"""Homestead fork definition."""

from typing import List, Sized, Tuple

from ethereum_test_base_types import AccessList, Address
from ethereum_test_base_types.conversions import BytesConvertible
from ethereum_test_forks.base_fork import (
    TransactionIntrinsicCostCalculator,
)
from ethereum_test_forks.forks.frontier.fork import Frontier
from ethereum_test_vm import EVMCodeType, Opcodes


class Homestead(Frontier):
    """Homestead fork."""

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """
        At Homestead, EC-recover, SHA256, RIPEMD160, and Identity pre-compiles
        are introduced.
        """
        return [Address(i) for i in range(1, 5)] + super(Homestead, cls).precompiles(
            block_number, timestamp
        )

    @classmethod
    def call_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """At Homestead, DELEGATECALL opcode was introduced."""
        return [(Opcodes.DELEGATECALL, EVMCodeType.LEGACY)] + super(Homestead, cls).call_opcodes(
            block_number, timestamp
        )

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return the list of Opcodes that are valid to work on this fork."""
        return [Opcodes.DELEGATECALL] + super(Homestead, cls).valid_opcodes()

    @classmethod
    def transaction_intrinsic_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionIntrinsicCostCalculator:
        """
        At Homestead, the transaction intrinsic cost needs to take contract
        creation into account.
        """
        super_fn = super(Homestead, cls).transaction_intrinsic_cost_calculator(
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
                access_list=access_list,
                authorization_list_or_count=authorization_list_or_count,
            )
            if contract_creation:
                intrinsic_cost += gas_costs.G_TRANSACTION_CREATE
            return intrinsic_cost

        return fn
