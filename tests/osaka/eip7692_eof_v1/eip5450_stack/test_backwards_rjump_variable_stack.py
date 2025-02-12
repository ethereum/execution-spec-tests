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
            name="backwards_rjump_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.POP
                    + Op.RJUMP[-5],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000045f6000e100025f5f5f50e0fffb",
        ),
        Container(
            name="backwards_rjump_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.POP
                    + Op.PUSH1[1]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.RJUMP[-11],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001504000000008000045f6000e100025f5f5f506001e10003e0fff8e0fff5",
        ),
        Container(
            name="backwards_rjump_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.POP
                    + Op.PUSH1[1]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.PUSH0
                    + Op.RJUMP[-12],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001604000000008000045f6000e100025f5f5f506001e10003e0fff85fe0fff4",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.PUSH1[0]
                    + Op.RJUMPI[1]
                    + Op.PUSH0
                    + Op.RJUMP[-7],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001104000000008000045f6000e100025f5f6000e100015fe0fff9",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_variable_stack_4",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.PUSH1[0]
                    + Op.RJUMPI[1]
                    + Op.POP
                    + Op.RJUMP[-7],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001104000000008000045f6000e100025f5f6000e1000150e0fff9",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_variable_stack_5",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.RJUMP[-4],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000045f6000e100025f5f5fe0fffc",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="backwards_rjump_variable_stack_6",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.POP
                    + Op.RJUMP[-4],
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000035f6000e100025f5f5f50e0fffc",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
    ],
    ids=lambda c: c.name,
)
def test_backwards_rjump_variable_stack(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test backwards RJUMP with variable stack."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
