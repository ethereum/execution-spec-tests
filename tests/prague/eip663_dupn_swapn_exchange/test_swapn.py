"""
abstract: Tests [EIP-663: SWAPN, DUPN and EXCHANGE instructions](https://eips.ethereum.org/EIPS/eip-663)
    Tests for the SWAPN instruction.
"""  # noqa: E501

import pytest

from ethereum_test_tools import Account, Environment, StateTestFiller, TestAddress, Transaction
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..eip3540_eof_v1.spec import EOF_FORK_NAME
from . import REFERENCE_SPEC_GIT_PATH, REFERENCE_SPEC_VERSION

REFERENCE_SPEC_GIT_PATH = REFERENCE_SPEC_GIT_PATH
REFERENCE_SPEC_VERSION = REFERENCE_SPEC_VERSION


@pytest.mark.valid_from(EOF_FORK_NAME)
def test_swapn_all_valid_immediates(
    tx: Transaction,
    state_test: StateTestFiller,
):
    """
    Test case for all valid SWAPN immediates.
    """
    n = 100
    values = range(0x500, 0x500 + 257)

    eof_code = Container(
        sections=[
            Section.Code(
                code=b"".join(Op.PUSH2(v) for v in values)
                + b"".join(Op.SWAPN(0xFF - x) + Op.PUSH2(x) + Op.SSTORE for x in range(0, n))
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=258,
            )
        ],
    )

    pre = {
        TestAddress: Account(balance=1_000_000_000),
        tx.to: Account(code=eof_code),
    }

    values_rotated = list(values[1:]) + [values[0]]
    post = {tx.to: Account(storage=dict(zip(range(0, n), reversed(values_rotated))))}

    state_test(
        env=Environment(),
        pre=pre,
        post=post,
        tx=tx,
    )
