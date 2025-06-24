"""
abstract: Tests worst-case scenarios for memory copy opcodes.

Tests running worst-case memory copy opcodes.
"""

import math
from typing import Optional

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Environment,
    Hash,
    StateTestFiller,
    Transaction,
    While,
    compute_create2_address,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import code_loop_precompile_call

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"


class CallDataOrigin:
    """Enum for calldata origins."""

    TRANSACTION = 1
    CALL = 2


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "origin",
    [
        pytest.param(CallDataOrigin.TRANSACTION, id="transaction"),
        pytest.param(CallDataOrigin.CALL, id="call"),
    ],
)
@pytest.mark.parametrize(
    "size",
    [
        pytest.param(0, id="0 bytes"),
        pytest.param(10, id="10 bytes"),
        pytest.param(100, id="100 bytes"),
        pytest.param(1 * 1024, id="1KiB"),
        pytest.param(10 * 1024, id="10KiB"),
        pytest.param(100 * 1024, id="100KiB"),
        pytest.param(1024 * 1024, id="1MiB"),
    ],
)
def test_worst_calldatacopy(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    origin: CallDataOrigin,
    size: int,
):
    """Test running a block filled with CALLDATACOPY executions."""
    env = Environment()
    max_code_size = fork.max_code_size()

    # We create the contract that will be doing the CALLDATACOPY multiple times.
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(Op.PUSH0)
    iter_block = Op.CALLDATACOPY(Op.PUSH0, Op.PUSH0, Op.CALLDATASIZE)
    max_iters_loop = (max_code_size - len(jumpdest) - len(jump_back)) // len(iter_block)
    code = jumpdest + sum([iter_block] * max_iters_loop) + jump_back
    if len(code) > max_code_size:
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {max_code_size}")
    code_address = pre.deploy_contract(code=code)

    tx_target = code_address
    if origin == CallDataOrigin.CALL:
        # If the origin is CALL, we need to create a contract that will call the
        # target contract with the calldata.
        code = Op.CALLDATACOPY(Op.PUSH0, Op.PUSH0, Op.CALLDATASIZE) + Op.STATICCALL(
            address=code_address, ret_size=Op.CALLDATASIZE
        )
        tx_target = pre.deploy_contract(code=code)

    tx = Transaction(
        to=tx_target,
        gas_limit=env.gas_limit,
        data=b"\xff" * size,
        sender=pre.fund_eoa(),
    )

    state_test(
        genesis_environment=env,
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "max_code_size_ratio",
    [
        pytest.param(0, id="0 bytes"),
        pytest.param(0.25, id="0.25x max code size"),
        pytest.param(0.50, id="0.50x max code size"),
        pytest.param(0.75, id="0.75x max code size"),
        pytest.param(1.00, id="max code size"),
    ],
)
def test_worst_codecopy(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    max_code_size_ratio: float,
):
    """Test running a block filled with CODECOPY executions."""
    env = Environment()
    max_code_size = fork.max_code_size()

    size = int(max_code_size * max_code_size_ratio)

    code_prefix = Op.PUSH32(size)
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(len(code_prefix))
    iter_block = Op.CODECOPY(Op.PUSH0, Op.PUSH0, Op.DUP1)
    max_iters_loop = (max_code_size - len(code_prefix) - len(jumpdest) - len(jump_back)) // len(
        iter_block
    )
    code = code_prefix + jumpdest + sum([iter_block] * max_iters_loop) + jump_back
    if len(code) > max_code_size:
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {max_code_size}")
    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=env.gas_limit,
        data=b"\xff" * size,
        sender=pre.fund_eoa(),
    )

    state_test(
        genesis_environment=env,
        pre=pre,
        post={},
        tx=tx,
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize(
    "size",
    [
        pytest.param(0, id="0 bytes"),
        pytest.param(10, id="10 bytes"),
        pytest.param(100, id="100 bytes"),
        pytest.param(1 * 1024, id="1KiB"),
        pytest.param(10 * 1024, id="10KiB"),
        pytest.param(100 * 1024, id="100KiB"),
        pytest.param(1024 * 1024, id="1MiB"),
    ],
)
def test_worst_returndatacopy(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    size: int,
):
    """Test running a block filled with RETURNDATACOPY executions."""
    env = Environment()
    max_code_size = fork.max_code_size()

    # Create the contract that will RETURN the data that will be used for RETURNDATACOPY.
    # Random-ish data is injected at different points in memory to avoid making the content
    # predictable. If `size` is 0, this helper contract won't be used.
    code = (
        Op.MSTORE8(0, Op.GAS)
        + Op.MSTORE8(size // 2, Op.GAS)
        + Op.MSTORE8(size - 1, Op.GAS)
        + Op.RETURN(0, size)
    )
    helper_contract = pre.deploy_contract(code=code)

    # We create the contract that will be doing the RETURNDATACOPY multiple times.
    code_prefix = Op.STATICCALL(address=helper_contract) if size > 0 else Bytecode()
    jumpdest = Op.JUMPDEST
    jump_back = Op.JUMP(len(code_prefix))
    iter_block = Op.RETURNDATACOPY(Op.PUSH0, Op.PUSH0, Op.RETURNDATASIZE)
    max_iters_loop = (max_code_size - len(code_prefix) - len(jumpdest) - len(jump_back)) // len(
        iter_block
    )
    code = code_prefix + jumpdest + sum([iter_block] * max_iters_loop) + jump_back
    if len(code) > max_code_size:
        raise ValueError(f"Code size {len(code)} exceeds maximum code size {max_code_size}")

    tx = Transaction(
        to=pre.deploy_contract(code=code),
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    state_test(
        genesis_environment=env,
        pre=pre,
        post={},
        tx=tx,
    )
