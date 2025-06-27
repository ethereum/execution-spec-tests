"""
abstract: Tests zkEVMs worst-case opcode scenarios.
    Tests zkEVMs worst-case opcode scenarios.

Tests running worst-case opcodes scenarios for zkEVMs.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_vm.opcode import Opcode

from .helpers import code_loop_precompile_call


@pytest.mark.parametrize(
    "opcode",
    [
        pytest.param(Op.LOG0, id="log0"),
        pytest.param(Op.LOG1, id="log1"),
        pytest.param(Op.LOG2, id="log2"),
        pytest.param(Op.LOG3, id="log3"),
        pytest.param(Op.LOG4, id="log4"),
    ],
)
@pytest.mark.parametrize(
    "size",
    [
        0,  # 0 bytes
        1024 * 1024,  # 1MiB
    ],
)
@pytest.mark.parametrize("empty_topic", [True, False])
@pytest.mark.parametrize("fixed_offset", [True, False])
def test_worst_log_opcodes(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    opcode: Opcode,
    empty_topic: bool,
    size: int,
    fixed_offset: bool,
):
    """Test running a block with as many LOG opcodes as possible."""
    env = Environment()
    max_code_size = fork.max_code_size()

    calldata = Op.PUSH0 if empty_topic else Op.PUSH32(2**256 - 1)

    topic_count = len(opcode.kwargs or []) - 2

    offset = Op.PUSH0 if fixed_offset else Op.MOD(Op.GAS, 7)

    code_sequence = Op.DUP1 * topic_count + Op.PUSH32(size) + offset + opcode

    code = code_loop_precompile_call(calldata, code_sequence, fork)
    assert len(code) <= max_code_size

    code_address = pre.deploy_contract(code=code)

    tx = Transaction(
        to=code_address,
        gas_limit=env.gas_limit,
        sender=pre.fund_eoa(),
    )

    state_test(
        env=env,
        pre=pre,
        post={},
        tx=tx,
    )
