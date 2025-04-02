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
            name="minimal_valid_eof1_multiple_code_sections_0",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x08,  # Types Length: 8
                    0x02,
                    0x00,
                    0x02,  # Code Sections (Length: 2)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x00,
                    0x01,  #   Code Section 1 (Length: 1)
                    # --- Error: Invalid Data Header ---#
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0xFE,
                    0xFE,
                ]
            ),
            expected_bytecode="ef000101000802000200010001000080000000800000fefe",
            validity_error=[EOFException.MISSING_DATA_SECTION],
        ),
        Container(
            name="minimal_valid_eof1_multiple_code_sections_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.POP + Op.CALLF[2] + Op.POP + Op.RETF,
                    code_inputs=1,
                    code_outputs=0,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.ADDRESS + Op.DUP1 + Op.CALLF[3] + Op.POP * 2 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.DUP1 + Op.RETF,
                    code_inputs=2,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010010020004000500060008000204000000008000010100000100010003020300035fe300010050e3000250e43080e300035050e480e4",
        ),
        Container(
            name="minimal_valid_eof1_multiple_code_sections_2",
            sections=[
                Section.Code(code=Op.JUMPF[1]),
                Section.Code(code=Op.INVALID),
                Section.Data(data="da"),
            ],
            expected_bytecode="ef000101000802000200030001040001000080000000800000e50001feda",
        ),
    ],
    ids=lambda c: c.name,
)
def test_minimal_valid_eof1_multiple_code_sections(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test a minimal valid EOF1 with multiple code sections."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
