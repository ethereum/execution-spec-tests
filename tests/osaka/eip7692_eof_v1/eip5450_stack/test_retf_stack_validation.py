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
            name="retf_stack_validation_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000802000200040003040000000080000200020002e30001005f5fe4",
        ),
        Container(
            name="retf_stack_validation_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef000101000802000200040002040000000080000200020001e30001005fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="retf_stack_validation_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="retf_stack_validation_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.RJUMPI[7] + Op.PUSH1[1] * 2 + Op.RJUMP[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
        ),
    ],
    ids=lambda c: c.name,
)
def test_retf_stack_validation(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test RETF stack validation."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
