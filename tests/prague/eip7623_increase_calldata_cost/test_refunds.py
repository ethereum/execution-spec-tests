"""
abstract: Test [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623)
    Test applied refunds for [EIP-7623: Increase calldata cost](https://eips.ethereum.org/EIPS/eip-7623).
"""  # noqa: E501

from enum import Enum, Flag, auto
from typing import Dict

import pytest

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import (
    Address,
    Alloc,
    Bytecode,
    StateTestFiller,
    Transaction,
    TransactionReceipt,
)
from ethereum_test_tools import Opcodes as Op

from .helpers import DataTestType
from .spec import ref_spec_7623

REFERENCE_SPEC_GIT_PATH = ref_spec_7623.git_path
REFERENCE_SPEC_VERSION = ref_spec_7623.version

ENABLE_FORK = Prague
pytestmark = [pytest.mark.valid_from(str(ENABLE_FORK))]


class RefundTestType(Enum):
    """Refund test type."""

    EXECUTION_GAS_MINUS_REFUND_GREATER_THAN_DATA_FLOOR = 0
    """
    The execution gas minus the refund is greater than the data floor, hence the execution gas cost
    is charged.
    """
    EXECUTION_GAS_MINUS_REFUND_LESS_THAN_DATA_FLOOR = 1
    """
    The execution gas minus the refund is less than the data floor, hence the data floor cost is
    charged.
    """


class RefundType(Flag):
    """Refund type."""

    STORAGE_CLEAR = auto()
    """The storage is cleared from a non-zero value."""

    AUTHORIZATION_EXISTING_AUTHORITY = auto()
    """The authorization list contains an authorization where the authority exists in the state."""


@pytest.fixture
def data_test_type() -> DataTestType:
    """Return data test type."""
    return DataTestType.FLOOR_GAS_COST_GREATER_THAN_INTRINSIC_GAS


@pytest.fixture
def authorization_refund(refund_type: RefundType) -> int:
    """Modify fixture from conftest to automatically read the refund_type information."""
    return RefundType.AUTHORIZATION_EXISTING_AUTHORITY in refund_type


@pytest.fixture
def ty(refund_type: RefundType) -> int:
    """Modify fixture from conftest to automatically read the refund_type information."""
    if RefundType.AUTHORIZATION_EXISTING_AUTHORITY in refund_type:
        return 4
    return 2


@pytest.fixture
def max_refund(fork: Fork, refund_type: RefundType) -> int:
    """Return the max refund gas of the transaction."""
    gas_costs = fork.gas_costs()
    max_refund = gas_costs.R_STORAGE_CLEAR if RefundType.STORAGE_CLEAR in refund_type else 0
    max_refund += (
        gas_costs.R_AUTHORIZATION_EXISTING_AUTHORITY
        if RefundType.AUTHORIZATION_EXISTING_AUTHORITY in refund_type
        else 0
    )
    return max_refund


@pytest.fixture
def prefix_code_gas(fork: Fork, refund_type: RefundType) -> int:
    """Return the minimum execution gas cost due to the refund type."""
    if RefundType.STORAGE_CLEAR in refund_type:
        # Minimum code to generate a storage clear is Op.SSTORE(0, 0).
        gas_costs = fork.gas_costs()
        return gas_costs.G_COLD_SLOAD + gas_costs.G_STORAGE_RESET + (gas_costs.G_VERY_LOW * 2)
    return 0


@pytest.fixture
def prefix_code(refund_type: RefundType) -> Bytecode:
    """Return the minimum execution gas cost due to the refund type."""
    if RefundType.STORAGE_CLEAR in refund_type:
        # Clear the storage to trigger a refund.
        return Op.SSTORE(0, 0)
    return Bytecode()


@pytest.fixture
def code_storage(refund_type: RefundType) -> Dict:
    """Return the minimum execution gas cost due to the refund type."""
    if RefundType.STORAGE_CLEAR in refund_type:
        # Pre-set the storage to be cleared.
        return {0: 1}
    return {}


@pytest.fixture
def execution_gas_used(
    tx_intrinsic_gas_cost_before_execution: int,
    tx_floor_data_cost: int,
    max_refund: int,
    prefix_code_gas: int,
    refund_test_type: RefundTestType,
) -> int:
    """
    Return the amount of gas that needs to be consumed by the execution.

    This gas amount is on top of the transaction intrinsic gas cost.

    Since intrinsic_gas_data_floor_minimum_delta is zero for all test cases, if this value is zero
    it will result in the refund being applied to the execution gas cost and the resulting amount
    being always below the floor data cost.
    """

    def execution_gas_cost(execution_gas: int) -> int:
        total_gas_used = tx_intrinsic_gas_cost_before_execution + execution_gas
        return total_gas_used - min(max_refund, total_gas_used // 5)

    execution_gas = prefix_code_gas

    assert execution_gas_cost(execution_gas) < tx_floor_data_cost, "tx_floor_data_cost is too low"

    # Dumb for-loop to find the execution gas cost that will result in the expected refund.
    while execution_gas_cost(execution_gas) < tx_floor_data_cost:
        execution_gas += 1
    if refund_test_type == RefundTestType.EXECUTION_GAS_MINUS_REFUND_GREATER_THAN_DATA_FLOOR:
        return execution_gas
    elif refund_test_type == RefundTestType.EXECUTION_GAS_MINUS_REFUND_LESS_THAN_DATA_FLOOR:
        return execution_gas - 1

    raise ValueError("Invalid refund test type")


@pytest.fixture
def refund(
    tx_intrinsic_gas_cost_before_execution: int,
    execution_gas_used: int,
    max_refund: int,
) -> int:
    """Return the refund gas of the transaction."""
    total_gas_used = tx_intrinsic_gas_cost_before_execution + execution_gas_used
    return min(max_refund, total_gas_used // 5)


@pytest.fixture
def to(
    pre: Alloc,
    execution_gas_used: int,
    prefix_code: Bytecode,
    prefix_code_gas: int,
    code_storage: Dict,
) -> Address | None:
    """Return a contract that consumes the expected execution gas."""
    return pre.deploy_contract(
        prefix_code + (Op.JUMPDEST * (execution_gas_used - prefix_code_gas)) + Op.STOP,
        storage=code_storage,
    )


@pytest.fixture
def tx_gas_limit(
    tx_intrinsic_gas_cost_including_floor_data_cost: int,
    tx_intrinsic_gas_cost_before_execution: int,
    execution_gas_used: int,
) -> int:
    """
    Gas limit for the transaction.

    The gas delta is added to the intrinsic gas cost to generate different test scenarios.
    """
    tx_gas_limit = tx_intrinsic_gas_cost_before_execution + execution_gas_used
    assert tx_gas_limit >= tx_intrinsic_gas_cost_including_floor_data_cost
    return tx_gas_limit


@pytest.mark.parametrize(
    "refund_test_type",
    [
        RefundTestType.EXECUTION_GAS_MINUS_REFUND_GREATER_THAN_DATA_FLOOR,
        RefundTestType.EXECUTION_GAS_MINUS_REFUND_LESS_THAN_DATA_FLOOR,
    ],
)
@pytest.mark.parametrize(
    "refund_type",
    [
        RefundType.STORAGE_CLEAR,
        RefundType.STORAGE_CLEAR | RefundType.AUTHORIZATION_EXISTING_AUTHORITY,
        RefundType.AUTHORIZATION_EXISTING_AUTHORITY,
    ],
)
def test_gas_refunds_from_data_floor(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    tx_floor_data_cost: int,
    tx_intrinsic_gas_cost_before_execution: int,
    execution_gas_cost: int,
    refund: int,
    refund_test_type: RefundTestType,
) -> None:
    """Test gas refunds deducted from the execution gas cost and not the data floor."""
    gas_used = tx_intrinsic_gas_cost_before_execution + execution_gas_cost - refund
    if refund_test_type == RefundTestType.EXECUTION_GAS_MINUS_REFUND_LESS_THAN_DATA_FLOOR:
        assert gas_used < tx_floor_data_cost
    elif refund_test_type == RefundTestType.EXECUTION_GAS_MINUS_REFUND_GREATER_THAN_DATA_FLOOR:
        assert gas_used >= tx_floor_data_cost
    else:
        raise ValueError("Invalid refund test type")
    if gas_used < tx_floor_data_cost:
        gas_used = tx_floor_data_cost
    tx.expected_receipt = TransactionReceipt(gas_used=gas_used)
    state_test(
        pre=pre,
        post={
            tx.to: {
                "storage": {0: 0},  # Verify storage was cleared
            }
        },
        tx=tx,
    )
