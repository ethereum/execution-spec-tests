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
            name="jumpf_to_returning_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(code=Op.JUMPF[2], code_outputs=2),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040003000304000000008000020002000000020002e3000100e500025f5fe4",
        ),
        Container(
            name="jumpf_to_returning_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040005000304000000008000020002000200020002e30001005f5fe500025f5fe4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="jumpf_to_returning_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=2,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040006000204000000008000020002000303020003e30001005f5f5fe5000250e4",
        ),
        Container(
            name="jumpf_to_returning_3",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 4 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=2,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040007000204000000008000020002000403020003e30001005f5f5f5fe5000250e4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="jumpf_to_returning_4",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=3,
                    code_outputs=2,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040005000204000000008000020002000203020003e30001005f5fe5000250e4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="jumpf_to_returning_5",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef000101000c02000300040004000204000000008000020002000100010001e30001005fe500025fe4",
        ),
        Container(
            name="jumpf_to_returning_6",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef000101000c02000300040006000204000000008000020002000300010001e30001005f5f5fe500025fe4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="jumpf_to_returning_7",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(code=Op.JUMPF[2], code_outputs=2, max_stack_height=0),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef000101000c02000300040003000204000000008000020002000000010001e3000100e500025fe4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="jumpf_to_returning_8",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 4 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.POP * 2 + Op.RETF,
                    code_inputs=3,
                    code_outputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040007000304000000008000020002000403010003e30001005f5f5f5fe500025050e4",
        ),
        Container(
            name="jumpf_to_returning_9",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 5 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=5,
                ),
                Section.Code(
                    code=Op.POP * 2 + Op.RETF,
                    code_inputs=3,
                    code_outputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040008000304000000008000020002000503010003e30001005f5f5f5f5fe500025050e4",
            validity_error=[EOFException.STACK_HIGHER_THAN_OUTPUTS],
        ),
        Container(
            name="jumpf_to_returning_10",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP * 2 + Op.RETF,
                    code_inputs=3,
                    code_outputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000c02000300040006000304000000008000020002000303010003e30001005f5f5fe500025050e4",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_jumpf_to_returning(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test JUMPF to returning function."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
