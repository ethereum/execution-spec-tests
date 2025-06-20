"""
abstract: Tests [EIP-7907 Meter Contract Code Size And Increase Limit](https://eips.ethereum.org/EIPS/eip-7907)
    Test cases for [EIP-7907 Meter Contract Code Size And Increase Limit](https://eips.ethereum.org/EIPS/eip-7907)].
"""

from typing import Generator

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    CodeGasMeasure,
    Conditional,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.utility.pytest import ParameterSet
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7907.md"
REFERENCE_SPEC_VERSION = "d758026fc3bd5ac21b652e73d244dee803b1fe44"

pytestmark = pytest.mark.valid_from("Prague")


def create_large_contract(
    *,
    size: int,
    padding_byte: bytes = b"\0",
    prefix: Bytecode | None = None,
) -> bytes:
    """Create a large contract with the given size and prefix."""
    if prefix is None:
        prefix = Bytecode()
    return bytes(prefix + padding_byte * (size - len(prefix)))


@pytest.fixture
def large_contract_code() -> Bytecode:
    """Return the default large contract code."""
    return Op.STOP


@pytest.fixture
def large_contract_size(fork: Fork) -> int:
    """Return the minimum contract size that triggers the large contract access gas."""
    large_contract_size = fork.large_contract_size()
    if large_contract_size is None:
        return fork.max_code_size()
    else:
        return large_contract_size + 1


@pytest.fixture
def large_contract_bytecode(
    large_contract_size: int,
    large_contract_code: Bytecode | None,
) -> bytes:
    """Return the default large contract code."""
    return create_large_contract(size=large_contract_size, prefix=large_contract_code)


@pytest.fixture
def large_contract_address(
    pre: Alloc,
    large_contract_bytecode: bytes,
) -> Address:
    """Create a large contract address."""
    return pre.deploy_contract(large_contract_bytecode)


def large_contract_size_cases(fork: Fork) -> Generator[ParameterSet, None, None]:
    """Return the default large contract size."""
    yield pytest.param(fork.max_code_size(), id="max_code_size")
    large_contract_size = fork.large_contract_size()
    if large_contract_size is not None:
        yield pytest.param(large_contract_size, id="large_contract_size")
        yield pytest.param(large_contract_size + 1, id="large_contract_size_plus_1")
        yield pytest.param(large_contract_size + 31, id="large_contract_size_plus_31")
        yield pytest.param(large_contract_size + 33, id="large_contract_size_plus_33")

        yield pytest.param(
            ((fork.max_code_size() - large_contract_size) // 2) + large_contract_size,
            id="half_max_code_size_minus_large_contract_size_plus_large_contract_size",
        )


@pytest.mark.parametrize_by_fork(
    "large_contract_size",
    large_contract_size_cases,
)
@pytest.mark.with_all_call_opcodes
def test_gas_on_call_to_large_contract(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    call_opcode: Op,
    large_contract_address: Address,
    large_contract_size: int,
):
    """Test calling a large contract with enough gas to execute the call."""
    gas_costs = fork.gas_costs()
    overhead_cost = (
        gas_costs.G_VERY_LOW * (call_opcode.popped_stack_items - 1)  # Call stack items
        + gas_costs.G_BASE  # Call gas
    )
    entry_point_code = CodeGasMeasure(
        code=call_opcode(address=large_contract_address),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=0,
    )
    entry_point_address = pre.deploy_contract(entry_point_code)

    large_contract_access_gas_calculator = fork.large_contract_access_gas_calculator()
    expected_gas_cost = gas_costs.G_COLD_ACCOUNT_ACCESS + large_contract_access_gas_calculator(
        size=large_contract_size,
    )

    tx = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=pre.fund_eoa(),
    )
    post = {
        entry_point_address: Account(
            storage={0: expected_gas_cost},
        )
    }
    state_test(pre=pre, tx=tx, post=post)


# TODO: Create small contract, self-destruct, recreate large contract, call it


def test_contract_reentry(
    state_test: StateTestFiller,
    pre: Alloc,
    large_contract_size: int,
):
    """
    Test a large contract being the transaction entry point, calls a different contract,
    and then re-enters the large contract back to the entry point.
    """
    intermediate_code = Op.SSTORE(0, Op.CALL(address=Op.CALLER, value=0)) + Op.STOP
    intermediate_address = pre.deploy_contract(intermediate_code)
    entry_point_code = (
        Conditional(
            condition=Op.ISZERO(Op.CALLVALUE),
            if_true=Op.STOP,
            if_false=Op.CALL(address=intermediate_address),
        )
        + Op.STOP
    )
    entry_large_contract_address = pre.deploy_contract(
        create_large_contract(
            size=large_contract_size,
            prefix=entry_point_code,
        )
    )

    tx = Transaction(
        to=entry_large_contract_address,
        value=1,
        gas_limit=100_000,
        sender=pre.fund_eoa(),
    )
    post = {
        intermediate_address: Account(
            storage={0: 1},
        )
    }

    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


def test_different_large_contracts_same_code_hash(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    large_contract_size: int,
):
    """
    Test calling two different large contracts with the same code hash in the
    same transaction.
    """
    gas_costs = fork.gas_costs()
    large_contract_bytecode = create_large_contract(size=large_contract_size)
    large_contract_address_1 = pre.deploy_contract(large_contract_bytecode)
    large_contract_address_2 = pre.deploy_contract(large_contract_bytecode)

    call_opcode = Op.CALL
    overhead_cost = (
        gas_costs.G_VERY_LOW * (call_opcode.popped_stack_items - 1)  # Call stack items
        + gas_costs.G_BASE  # Call gas
    )
    entry_point_code = CodeGasMeasure(
        code=call_opcode(address=large_contract_address_1),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=0,
        stop=False,
    ) + CodeGasMeasure(
        code=call_opcode(address=large_contract_address_2),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=1,
    )
    entry_point_address = pre.deploy_contract(entry_point_code)

    large_contract_access_gas_calculator = fork.large_contract_access_gas_calculator()
    expected_gas_cost = gas_costs.G_COLD_ACCOUNT_ACCESS + large_contract_access_gas_calculator(
        size=large_contract_size,
    )

    tx = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=pre.fund_eoa(),
    )
    post = {
        entry_point_address: Account(
            storage={0: expected_gas_cost, 1: expected_gas_cost},
        )
    }
    state_test(pre=pre, tx=tx, post=post)


def test_calling_large_contract_twice_same_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    large_contract_address: Address,
    large_contract_size: int,
):
    """Test calling a large contract twice in the same transaction."""
    gas_costs = fork.gas_costs()
    call_opcode = Op.CALL
    overhead_cost = (
        gas_costs.G_VERY_LOW * (call_opcode.popped_stack_items - 1)  # Call stack items
        + gas_costs.G_BASE  # Call gas
    )
    entry_point_code = CodeGasMeasure(
        code=call_opcode(address=large_contract_address),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=0,
        stop=False,
    ) + CodeGasMeasure(
        code=call_opcode(address=large_contract_address),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=1,
    )
    entry_point_address = pre.deploy_contract(entry_point_code)

    large_contract_access_gas_calculator = fork.large_contract_access_gas_calculator()
    expected_gas_cost = gas_costs.G_COLD_ACCOUNT_ACCESS + large_contract_access_gas_calculator(
        size=large_contract_size,
    )

    tx = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=pre.fund_eoa(),
    )
    post = {
        entry_point_address: Account(
            storage={0: expected_gas_cost, 1: gas_costs.G_WARM_ACCOUNT_ACCESS},
        )
    }
    state_test(pre=pre, tx=tx, post=post)


def test_calling_large_contract_twice_different_tx(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    large_contract_address: Address,
    large_contract_size: int,
):
    """Test calling a large contract in different transactions in the same block."""
    gas_costs = fork.gas_costs()
    call_opcode = Op.CALL
    overhead_cost = (
        gas_costs.G_VERY_LOW * (call_opcode.popped_stack_items - 1)  # Call stack items
        + gas_costs.G_BASE  # Call gas
    )
    entry_point_code = (
        CodeGasMeasure(
            code=call_opcode(address=large_contract_address),
            overhead_cost=overhead_cost,
            extra_stack_items=1,
            sstore_key=Op.SLOAD(0),
            stop=False,
        )
        + Op.SSTORE(0, Op.ADD(Op.SLOAD(0), 1))
        + Op.STOP
    )
    entry_point_address = pre.deploy_contract(entry_point_code, storage={0: 1})

    large_contract_access_gas_calculator = fork.large_contract_access_gas_calculator()
    expected_gas_cost = gas_costs.G_COLD_ACCOUNT_ACCESS + large_contract_access_gas_calculator(
        size=large_contract_size,
    )
    sender = pre.fund_eoa()
    tx_1 = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=sender,
    )
    tx_2 = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=sender,
    )
    post = {
        entry_point_address: Account(
            storage={0: 3, 1: expected_gas_cost, 2: expected_gas_cost},
        )
    }
    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[tx_1, tx_2])],
        post=post,
    )


@pytest.mark.parametrize(
    "opcode,large_contract_cost_charged",
    [
        (Op.EXTCODESIZE, True),
        (Op.EXTCODEHASH, True),
        (Op.EXTCODECOPY, False),
        (Op.BALANCE, True),
        (Op.SELFDESTRUCT, True),
    ],
)
def test_opcode_then_call_large_contract(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    opcode: Op,
    large_contract_address: Address,
    large_contract_size: int,
    large_contract_cost_charged: bool,
):
    """
    Test calling a large contract after an opcode that accesses the account or code.

    - EXTCODESIZE
    - EXTCODEHASH
    - EXTCODECOPY
    - BALANCE
    - SELFDESTRUCT

    """
    gas_costs = fork.gas_costs()
    if opcode == Op.EXTCODECOPY:
        opcode_contract_code = opcode(
            address=large_contract_address,
            dest_offset=0,
            offset=0,
            size=1,
        )
    else:
        opcode_contract_code = opcode(address=large_contract_address)
    opcode_contract = pre.deploy_contract(opcode_contract_code, balance=1)

    call_opcode = Op.CALL
    overhead_cost = (
        gas_costs.G_VERY_LOW * (call_opcode.popped_stack_items - 1)  # Call stack items
        + gas_costs.G_BASE  # Call gas
    )
    entry_point_code = Op.SSTORE(0, call_opcode(address=opcode_contract)) + CodeGasMeasure(
        code=call_opcode(address=large_contract_address),
        overhead_cost=overhead_cost,
        extra_stack_items=1,
        sstore_key=1,
    )
    entry_point_address = pre.deploy_contract(entry_point_code)

    large_contract_access_gas_calculator = fork.large_contract_access_gas_calculator()
    expected_gas_cost = gas_costs.G_WARM_ACCOUNT_ACCESS
    if large_contract_cost_charged:
        expected_gas_cost += large_contract_access_gas_calculator(
            size=large_contract_size,
        )

    tx = Transaction(
        to=entry_point_address,
        gas_limit=1_000_000,
        sender=pre.fund_eoa(),
    )
    post = {
        entry_point_address: Account(
            storage={0: 1, 1: expected_gas_cost},
        )
    }
    state_test(pre=pre, tx=tx, post=post)


@pytest.mark.skip(reason="Not implemented")
def test_calling_large_contract_after_creation(state_test: StateTestFiller):
    """Test calling a large contract after it has been created (in the same transaction)."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_calling_large_contract_in_authorization_list(state_test: StateTestFiller):
    """Test calling a large contract in the authorization list of the transaction."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_calling_large_contract_in_access_list(state_test: StateTestFiller):
    """Test calling a large contract in the access list of the transaction."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_call_large_contract_then_opcode(state_test: StateTestFiller):
    """Test using an opcode that accesses the account or code after calling a large contract."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_call_large_contract_as_coinbase(state_test: StateTestFiller):
    """Test calling a large contract as the coinbase."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_call_delegated_account_to_large_contract(state_test: StateTestFiller):
    """Test calling a large contract from a delegated account."""
    pass


@pytest.mark.skip(reason="Not implemented")
def test_call_large_contract_after_oog_call_to_same_contract(state_test: StateTestFiller):
    """Test calling a large contract after an OOG call to the same contract."""
    pass
