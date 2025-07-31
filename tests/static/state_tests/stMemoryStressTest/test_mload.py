"""
Test MLOAD bounds checking with large memory offset.

This test verifies that MLOAD operations with large memory offsets
work correctly and don't cause out-of-gas errors when sufficient gas is provided.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Account, Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


# Ported from MLOAD_Bounds3Filler.json
@pytest.mark.valid_from("Cancun")
def test_mload_bounds3(state_test: StateTestFiller, pre: Alloc, env: Environment, fork: Fork):
    """Test MLOAD with large memory offset."""
    tx_gas_limit = fork.transaction_gas_limit_cap() or env.gas_limit

    memory_expansion_gas_calculator = fork.memory_expansion_gas_calculator()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    extra_gas = 100
    gas_available = tx_gas_limit - intrinsic_gas_cost_calc() - extra_gas

    offset, curr_offset = 0, 0

    while memory_expansion_gas_calculator(new_bytes=curr_offset) < gas_available:
        offset = curr_offset
        curr_offset += 100

    target_contract = pre.deploy_contract(code=Op.MLOAD(offset))

    tx = Transaction(
        gas_limit=tx_gas_limit,
        sender=pre.fund_eoa(),
        to=target_contract,
        value=1,
    )

    post = {
        target_contract: Account(
            balance=1,
        )
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


# Ported from MLOAD_Bounds2Filler.json
@pytest.mark.valid_from("Cancun")
def test_mload_bounds2(state_test: StateTestFiller, pre: Alloc, env: Environment, fork: Fork):
    """Test MLOAD with extremely large memory offsets."""
    tx_gas_limit = fork.transaction_gas_limit_cap() or env.gas_limit

    memory_expansion_gsc = fork.memory_expansion_gas_calculator()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    extra_gas = 100
    gas_available = tx_gas_limit - intrinsic_gas_cost_calc() - extra_gas

    offset, curr_offset = 0, 0

    while (
        memory_expansion_gsc(new_bytes=curr_offset)
        + memory_expansion_gsc(new_bytes=curr_offset * 2)
        + memory_expansion_gsc(new_bytes=curr_offset * 4)
    ) < gas_available:
        offset = curr_offset
        curr_offset += 100

    target_contract = pre.deploy_contract(
        code=(Op.MLOAD(offset) + Op.MLOAD(offset * 2) + Op.MLOAD(offset * 4)),
    )

    tx = Transaction(
        gas_limit=tx_gas_limit,
        sender=pre.fund_eoa(),
        to=target_contract,
        value=1,
    )

    post = {
        target_contract: Account(
            balance=1,
        )
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


# Ported from MLOAD_BoundsFiller.json
@pytest.mark.valid_from("Cancun")
def test_mload_bounds(state_test: StateTestFiller, pre: Alloc, env: Environment, fork: Fork):
    """Test MLOAD with bounds checking."""
    tx_gas_limit = fork.transaction_gas_limit_cap() or env.gas_limit

    memory_expansion_gas_calculator = fork.memory_expansion_gas_calculator()
    intrinsic_gas_cost_calc = fork.transaction_intrinsic_cost_calculator()
    extra_gas = 100
    gas_available = tx_gas_limit - intrinsic_gas_cost_calc() - extra_gas

    offset, curr_offset = 0, 0

    while memory_expansion_gas_calculator(new_bytes=curr_offset) < gas_available:
        offset = curr_offset
        curr_offset += 100

    target_contract = pre.deploy_contract(
        code=(Op.MLOAD(0) + Op.MLOAD(offset)),
    )

    tx = Transaction(
        gas_limit=tx_gas_limit,
        sender=pre.fund_eoa(),
        to=target_contract,
        value=1,
    )

    post = {
        target_contract: Account(
            balance=1,
        )
    }

    state_test(env=env, pre=pre, post=post, tx=tx)
