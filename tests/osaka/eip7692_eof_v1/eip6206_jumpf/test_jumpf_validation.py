"""EOF validation tests for JUMPF instruction."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .. import EOF_FORK_NAME
from ..eip4750_functions.test_code_validation import MAX_RUNTIME_OPERAND_STACK_HEIGHT

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "2f365ea0cd58faa6e26013ea77ce6d538175f7d0"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="to_0",
            sections=[
                Section.Code(
                    Op.CALLF[1] + Op.STOP,
                ),
                Section.Code(
                    Op.JUMPF[0],
                    code_outputs=0,
                ),
            ],
        ),
        Container(
            name="to_2",
            sections=[
                Section.Code(
                    Op.CALLF[1] + Op.STOP,
                ),
                Section.Code(
                    Op.JUMPF[2],
                    code_outputs=0,
                ),
                Section.Code(
                    Op.INVALID,
                ),
            ],
        ),
        Container(
            name="to_retf",
            sections=[
                Section.Code(
                    Op.CALLF[1] + Op.STOP,
                ),
                Section.Code(
                    Op.JUMPF[2],
                    code_outputs=0,
                ),
                Section.Code(
                    Op.RETF,
                ),
            ],
        ),
    ],
    ids=lambda container: container.name,
)
def test_returning_jumpf(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test cases for JUMPF instruction validation in a returning sections."""
    eof_test(container=container, expect_exception=EOFException.INVALID_NON_RETURNING_FLAG)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="jumpf1",
            sections=[
                Section.Code(
                    Op.JUMPF[1],
                )
            ],
        ),
        Container(
            name="jumpf2",
            sections=[
                Section.Code(
                    Op.JUMPF[2],
                ),
                Section.Code(
                    Op.STOP,
                ),
            ],
        ),
        Container(
            name="jumpf1_jumpf2",
            sections=[
                Section.Code(
                    Op.JUMPF[1],
                ),
                Section.Code(
                    Op.JUMPF[2],
                ),
            ],
        ),
    ],
    ids=lambda container: container.name,
)
def test_invalid_code_section_index(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test cases for JUMPF instructions with invalid target code section index."""
    eof_test(container=container, expect_exception=EOFException.INVALID_CODE_SECTION_INDEX)


def test_returning_section_aborts_jumpf(
    eof_test: EOFTestFiller,
):
    """
    Test EOF container validation where in the same code section we have returning
    and nonreturning terminating instructions.
    """
    container = Container(
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RJUMPI[4] + Op.POP + Op.JUMPF[2] + Op.RETF,
                code_outputs=1,
            ),
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RJUMPI[1] + Op.RETF + Op.INVALID,
                code_inputs=0,
                code_outputs=1,
            ),
        ],
    )
    eof_test(container=container)


@pytest.mark.parametrize("stack_height", [512, 513, 1023])
def test_jumpf_self_stack_overflow(eof_test: EOFTestFiller, stack_height: int):
    """Test JUMPF instruction jumping to itself causing validation time stack overflow."""
    container = Container(
        sections=[
            Section.Code(
                code=(Op.PUSH0 * stack_height) + Op.JUMPF[0],
                max_stack_height=stack_height,
            ),
        ],
    )
    stack_overflow = stack_height > MAX_RUNTIME_OPERAND_STACK_HEIGHT // 2
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize("stack_height_other", [1, 2, 512, 513, 1023])
@pytest.mark.parametrize("stack_height", [1, 2, 512, 513, 1023])
def test_jumpf_other_stack_overflow(
    eof_test: EOFTestFiller, stack_height: int, stack_height_other: int
):
    """Test JUMPF instruction jumping to other section causing validation time stack overflow."""
    container = Container(
        sections=[
            Section.Code(
                code=(Op.PUSH0 * stack_height) + Op.JUMPF[1],
                max_stack_height=stack_height,
            ),
            Section.Code(
                code=(Op.PUSH0 * stack_height_other) + Op.STOP,
                max_stack_height=stack_height_other,
            ),
        ],
    )
    stack_overflow = stack_height + stack_height_other > MAX_RUNTIME_OPERAND_STACK_HEIGHT
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="underflow_2",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=0,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040003000204000000008000020002000001020002e3000100e500025fe4",
        ),
        Container(
            name="underflow_3",
            sections=[
                Section.Code(
                    code=Op.JUMPF[1],
                ),
                Section.Code(
                    code=Op.REVERT(0, 0),
                    code_inputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200030005040000000080000001800003e5000160006000fd",
        ),
        Container(
            name="underflow_variable_stack_4",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP + Op.POP + Op.RETF,
                    code_inputs=5,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c0200030004000b000304000000008000030003000305030003e30001005f6000e100025f5fe500025050e4",
        ),
        Container(
            name="underflow_variable_stack_6",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.REVERT(0, 0),
                    code_inputs=4,
                    max_stack_height=6,
                ),
            ],
        ),
        Container(
            name="underflow_variable_stack_7",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.REVERT(0, 0),
                    code_inputs=3,
                    max_stack_height=5,
                ),
            ],
        ),
    ],
    ids=lambda x: x.name,
)
def test_jumpf_stack_underflow_examples(eof_test: EOFTestFiller, container: Container):
    """Test JUMPF instruction causing validation time stack underflow."""
    eof_test(container=container, expect_exception=EOFException.STACK_UNDERFLOW)
