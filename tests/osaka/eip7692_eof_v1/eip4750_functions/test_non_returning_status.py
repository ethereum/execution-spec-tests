"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "14400434e1199c57d912082127b1d22643788d11"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="non_returning_status_0",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.STOP),
            ],
            expected_bytecode="ef000101000802000200030001040000000080000000800000e5000100",
        ),
        Container(
            name="non_returning_status_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP),
                Section.Code(code=Op.JUMPF[2], code_outputs=0),
                Section.Code(code=Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300040003000104000000008000000000000000000000e3000100e50002e4",
        ),
        Container(
            name="non_returning_status_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[2],
                    code_inputs=1,
                    code_outputs=0,
                    max_stack_height=1,
                ),
                Section.Code(code=Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c020003000500070001040000000080000101000001000000005fe3000100e10001e4e50002e4",
        ),
        Container(
            name="non_returning_status_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[0],
                    code_inputs=1,
                    code_outputs=0,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010008020002000500070400000000800001010000015fe3000100e10001e4e50000",
        ),
        Container(
            name="non_returning_status_4",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[0], code_outputs=0),
            ],
            expected_bytecode="ef000101000802000200030003040000000080000000000000e50001e50000",
            validity_error=[EOFException.INVALID_NON_RETURNING_FLAG],
        ),
        Container(
            name="non_returning_status_5",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.JUMPF[1], max_stack_height=1),
                Section.Code(
                    code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[2],
                    code_inputs=1,
                    max_stack_height=1,
                ),
                Section.Code(code=Op.RETF, code_outputs=0),
            ],
            expected_bytecode="ef000101000c020003000400070001040000000080000101800001000000005fe50001e10001e4e50002e4",
            validity_error=[EOFException.INVALID_NON_RETURNING_FLAG],
        ),
        Container(
            name="non_returning_status_6",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.JUMPF[1], max_stack_height=1),
                Section.Code(
                    code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[0],
                    code_inputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010008020002000400070400000000800001018000015fe50001e10001e4e50000",
            validity_error=[EOFException.INVALID_NON_RETURNING_FLAG],
        ),
        Container(
            name="non_returning_status_7",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.JUMPF[2]),
                Section.Code(code=Op.JUMPF[1]),
            ],
            expected_bytecode="ef000101000c02000300030003000304000000008000000080000000800000e50001e50002e50001",
        ),
        Container(
            name="non_returning_status_8",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP),
                Section.Code(code=Op.JUMPF[2], code_outputs=0),
                Section.Code(code=Op.JUMPF[1], code_outputs=0),
            ],
            expected_bytecode="ef000101000c02000300040003000304000000008000000000000000000000e3000100e50002e50001",
        ),
    ],
    ids=lambda c: c.name,
)
def test_non_returning_status(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contracts containing code sections marked with non-returning status (0x80)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
