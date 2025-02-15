"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="backwards_rjump_0",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.RJUMP[-5], max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000504000000008000015f50e0fffb",
        ),
        Container(
            name="backwards_rjump_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.POP
                    + Op.PUSH1[1]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.RJUMP[-11],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000015f506001e10003e0fff8e0fff5",
        ),
        Container(
            name="backwards_rjump_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.POP
                    + Op.PUSH1[1]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.PUSH0
                    + Op.RJUMP[-12],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000015f506001e10003e0fff85fe0fff4",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_3",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.RJUMP[-4], max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000404000000008000015fe0fffc",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_4",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.RJUMP[-4], max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000504000000008000015f50e0fffc",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
    ],
    ids=lambda c: c.name,
)
def test_backwards_rjump(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test backwards RJUMP."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
