"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools.eof.v1 import Container

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="unknown_section_0",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    # --- Error: Invalid Types Header ---#
                    0x05,
                    0x00,
                    0x01,
                    0x00,
                    0xFE,
                ]
            ),
            expected_bytecode="ef000105000100fe",
            validity_error=[EOFException.MISSING_TYPE_HEADER],
        ),
        Container(
            name="unknown_section_1",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    # --- Error: Invalid Types Header ---#
                    0xFF,
                    0x00,
                    0x01,
                    0x00,
                    0xFE,
                ]
            ),
            expected_bytecode="ef0001ff000100fe",
            validity_error=[EOFException.MISSING_TYPE_HEADER],
        ),
        Container(
            name="unknown_section_2",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x01, #   Code Section 0 (Length: 1)
                    # --- Error: Invalid Data Header ---#
                    0x05,
                    0x00,
                    0x01,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0xFE,
                    0x00,
                ]
            ),
            expected_bytecode="ef000101000402000100010500010000800000fe00",
            validity_error=[EOFException.MISSING_DATA_SECTION],
        ),
        Container(
            name="unknown_section_3",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x01, #   Code Section 0 (Length: 1)
                    # --- Error: Invalid Data Header ---#
                    0xFF,
                    0x00,
                    0x01,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0xFE,
                    0x00,
                ]
            ),
            expected_bytecode="ef00010100040200010001ff00010000800000fe00",
            validity_error=[EOFException.MISSING_DATA_SECTION],
        ),
        Container(
            name="unknown_section_4",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x01, #   Code Section 0 (Length: 1)
                    0x04, 0x00, 0x01, # Data Length: 1
                    # --- Error: Invalid Terminator ---#
                    0x05,
                    0x00,
                    0x01,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0xFE,
                    0xAA,
                    0x00,
                ]
            ),
            expected_bytecode="ef000101000402000100010400010500010000800000feaa00",
            validity_error=[EOFException.MISSING_TERMINATOR],
        ),
        Container(
            name="unknown_section_5",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x01, #   Code Section 0 (Length: 1)
                    0x04, 0x00, 0x01, # Data Length: 1
                    # --- Error: Invalid Terminator ---#
                    0xFF,
                    0x00,
                    0x01,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x00,
                    0xFE,
                    0xAA,
                    0x00,
                ]
            ),
            expected_bytecode="ef00010100040200010001040001ff00010000800000feaa00",
            validity_error=[EOFException.MISSING_TERMINATOR],
        ),
    ],
    ids=lambda c: c.name,
)
def test_unknown_section(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contracts containing undefined sections."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
