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
            name="jumpf_to_nonreturning_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=5, max_stack_height=5),
            ],
            expected_bytecode="ef0001010008020002000b00010400000000800003058000055f6000e100025f5fe50001fe",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=3, max_stack_height=3),
            ],
            expected_bytecode="ef0001010008020002000b00010400000000800003038000035f6000e100025f5fe50001fe",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=1, max_stack_height=1),
            ],
            expected_bytecode="ef0001010008020002000b00010400000000800003018000015f6000e100025f5fe50001fe",
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID),
            ],
            expected_bytecode="ef0001010008020002000b00010400000000800003008000005f6000e100025f5fe50001fe",
        ),
    ],
    ids=lambda c: c.name,
)
def test_jumpf_to_nonreturning_variable_stack(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test JUMPF to non-returning function (variable stack)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
