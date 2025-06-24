"""
abstract: Tests worst-case scenarios for memory copy opcodes.

Tests running worst-case memory copy opcodes.
"""

import math

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
            Op.GAS, code_address, 0, Op.CALLDATASIZE, 0, 0
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
