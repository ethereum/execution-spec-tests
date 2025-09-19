"""
abstract: Tests benchmark worst-case bloatnet scenarios.
    Tests benchmark worst-case bloatnet scenarios.

Tests running worst-case bloatnet scenarios for benchmarking purposes.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Alloc,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.mark.parametrize(
    "calldata",
    [
        pytest.param(b"", id="empty"),
        pytest.param(b"\x00", id="zero-loop"),
        pytest.param(b"\x00" * 31 + b"\x20", id="one-loop"),
    ],
)
@pytest.mark.bloatnet
def test_worst_calldataload(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    calldata: bytes,
    gas_benchmark_value: int,
):
    """Test running a block with as many CALLDATALOAD as possible."""
    max_code_size = fork.max_code_size()

    code_prefix = Op.PUSH0 + Op.JUMPDEST
    code_suffix = Op.PUSH1(1) + Op.JUMP
    code_body_len = max_code_size - len(code_prefix) - len(code_suffix)
    code_loop_iter = Op.CALLDATALOAD
    code_body = code_loop_iter * (code_body_len // len(code_loop_iter))
    code = code_prefix + code_body + code_suffix
    assert len(code) <= max_code_size

    tx = Transaction(
        to=pre.deploy_contract(code=code),
        data=calldata,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    state_test(
        pre=pre,
        post={},
        tx=tx,
    )
