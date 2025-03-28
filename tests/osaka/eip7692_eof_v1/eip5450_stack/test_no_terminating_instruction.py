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
            name="no_terminating_instruction_0",
            sections=[
                Section.Code(code=Op.PUSH0, max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000005f",
            validity_error=[EOFException.MISSING_STOP_OPCODE],
        ),
        Container(
            name="no_terminating_instruction_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[2] + Op.PUSH1[1] + Op.ADD,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006002600101",
            validity_error=[EOFException.MISSING_STOP_OPCODE],
        ),
        Container(
            name="no_terminating_instruction_2",
            sections=[
                Section.Code(code=Op.PUSH1[1] + Op.RJUMPI[-5], max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006001e1fffb",
            validity_error=[EOFException.MISSING_STOP_OPCODE],
        ),
    ],
    ids=lambda c: c.name,
)
def test_no_terminating_instruction(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contract without a terminating instruction."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
