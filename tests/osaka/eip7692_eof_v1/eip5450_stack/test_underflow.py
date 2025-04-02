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
            name="underflow_0",
            sections=[
                Section.Code(code=Op.ADD + Op.STOP, max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000000100",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000802000200040002040000000080000101020002e30001005fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(code=Op.JUMPF[2], code_outputs=2, max_stack_height=0),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040003000204000000008000020002000001020002e3000100e500025fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.LOG2 + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000035f6000e100025f5fa200",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.ADD + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000035f6000e100025f5f0100",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.CALLF[1]
                    + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=4,
                    code_outputs=5,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010008020002000c00020400000000800004040500055f6000e100025f5fe30001005fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.CALLF[1]
                    + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=3,
                    code_outputs=4,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010008020002000c00020400000000800004030400045f6000e100025f5fe30001005fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_4",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP * 2 + Op.RETF,
                    code_inputs=5,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c0200030004000b000304000000008000030003000305030003e30001005f6000e100025f5fe500025050e4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_5",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=0,
                ),
                Section.Code(
                    code=Op.PUSH1[0] * 2 + Op.REVERT,
                    code_inputs=5,
                    max_stack_height=7,
                ),
            ],
            expected_bytecode="ef0001010008020002000b00050400000000800000058000075f6000e100025f5fe5000160006000fd",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_variable_stack_6",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=0,
                ),
                Section.Code(
                    code=Op.PUSH1[0] * 2 + Op.REVERT,
                    code_inputs=3,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010008020002000b00050400000000800000038000055f6000e100025f5fe5000160006000fd",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="underflow_3",
            sections=[
                Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                Section.Code(
                    code=Op.PUSH1[0] * 2 + Op.REVERT,
                    code_inputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200030005040000000080000001800003e5000160006000fd",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_underflow(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test stack underflow."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
