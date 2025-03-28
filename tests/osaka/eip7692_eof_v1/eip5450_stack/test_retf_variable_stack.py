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
            name="retf_variable_stack_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=5),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=5,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040009040000000080000500050003e30001005f6000e100025f5fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="retf_variable_stack_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040009040000000080000300030003e30001005f6000e100025f5fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="retf_variable_stack_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040009040000000080000100010003e30001005f6000e100025f5fe4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="retf_variable_stack_3",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=0,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040009040000000080000000000003e30001005f6000e100025f5fe4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
    ],
    ids=lambda c: c.name,
)
def test_retf_variable_stack(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test RETF stack validation (variable stack)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
