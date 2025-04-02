"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="invalid_section_0_type_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=0,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000204000000000000005fe4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.TLOAD,
                    code_outputs=1,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef00010100040200010003040000000001000060005c",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=127,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000204000000007f00005fe4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=129,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000204000000008100005fe4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_4",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=255,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef000101000402000100020400000000ff00005fe4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_5",
            sections=[
                Section.Code(code=Op.POP + Op.RETF, code_inputs=1, max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010002040000000180000050e4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_6",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.TLOAD,
                    code_inputs=2,
                    code_outputs=3,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef00010100040200010003040000000203000060005c",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_7",
            sections=[
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=128,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef00010100040200010002040000008080000050e4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
        Container(
            name="invalid_section_0_type_8",
            sections=[
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=255,
                    max_stack_height=0,
                ),
            ],
            expected_bytecode="ef0001010004020001000204000000ff80000050e4",
            validity_error=[EOFException.INVALID_FIRST_SECTION_TYPE],
        ),
    ],
    ids=lambda c: c.name,
)
def test_first_code_section_type(
    eof_test: EOFTestFiller,
    container: Container,
):
    """First code section should have 0 inputs and the Non Returning Function value (0x80)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
