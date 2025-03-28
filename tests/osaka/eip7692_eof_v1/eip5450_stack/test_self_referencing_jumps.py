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
            name="self_referencing_jumps_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.RJUMPI[-3] + Op.STOP,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006000e1fffd00",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="self_referencing_jumps_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.RJUMPV[-4] + Op.STOP,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006000e200fffc00",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="self_referencing_jumps_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.PUSH1[0]
                    + Op.RJUMPI[-3]
                    + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffd00",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
        Container(
            name="self_referencing_jumps_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.PUSH1[0]
                    + Op.RJUMPV[-4]
                    + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000045f6000e100025f5f6000e200fffc00",
            validity_error=[EOFException.STACK_HEIGHT_MISMATCH],
        ),
    ],
    ids=lambda c: c.name,
)
def test_self_referencing_jumps(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test rjump/rjumpi/rjumpv jumping to themselves."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
