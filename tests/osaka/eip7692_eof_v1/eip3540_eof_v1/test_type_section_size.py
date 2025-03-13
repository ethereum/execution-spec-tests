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
            name="types_section_0_size_0",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x00,  # Types Length: 0
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # --- Error: Code and Type sections mismatch ---#
                    # Code Section 0
                    0xFE,  #  [0] INVALID
                ]
            ),
            expected_bytecode="ef0001010000020001000104000000fe",
            validity_error=[EOFException.ZERO_SECTION_SIZE],
        ),
        Container(
            name="types_section_0_size_1",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x00,  # Types Length: 0
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x04,
                    0x00,
                    0x01,  # Data Length: 1
                    0x00,  # Terminator
                    # --- Error: Code and Type sections mismatch ---#
                    # Code Section 0
                    0xFE,  #  [0] INVALID
                    # Data Section
                    0xDA,
                ]
            ),
            expected_bytecode="ef0001010000020001000104000100feda",
            validity_error=[EOFException.ZERO_SECTION_SIZE],
        ),
        Container(
            name="invalid_type_section_size_0",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x01,  # Types Length: 1
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # --- Error: Invalid Types Content ---#
                    0x00,
                    0xFE,
                ]
            ),
            expected_bytecode="ef000101000102000100010400000000fe",
            validity_error=[EOFException.INVALID_TYPE_SECTION_SIZE],
        ),
        Container(
            name="invalid_type_section_size_1",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x02,  # Types Length: 2
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # --- Error: Invalid Types Content ---#
                    0x00,
                    0x80,
                    0xFE,
                ]
            ),
            expected_bytecode="ef00010100020200010001040000000080fe",
            validity_error=[EOFException.INVALID_TYPE_SECTION_SIZE],
        ),
        Container(
            name="invalid_type_section_size_2",
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
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # Code Section 0 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # Code Section 1 types
                    0x00,  #   Inputs: 0
                    0x00,  #   Outputs: 0
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # --- Error: Code and Type sections mismatch ---#
                    # Code Section 0
                    0xFE,  #  [0] INVALID
                ]
            ),
            expected_bytecode="ef00010100080200010001040000000080000000000000fe",
            validity_error=[EOFException.INVALID_TYPE_SECTION_SIZE],
        ),
        Container(
            name="invalid_type_section_size_3",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x10,  # Types Length: 16
                    0x02,
                    0x00,
                    0x03,  # Code Sections (Length: 3)
                    0x00,
                    0x01,  #   Code Section 0 (Length: 1)
                    0x00,
                    0x01,  #   Code Section 1 (Length: 1)
                    0x00,
                    0x01,  #   Code Section 2 (Length: 1)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # Code Section 0 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # Code Section 1 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # Code Section 2 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # Code Section 3 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x00,  #   Max Stack Height: 0
                    # --- Error: Code and Type sections mismatch ---#
                    # Code Section 0
                    0xFE,  #  [0] INVALID                  # Code Section 1
                    0xFE,  #  [0] INVALID                  # Code Section 2
                    0xFE,  #  [0] INVALID
                ]
            ),
            expected_bytecode="ef00010100100200030001000100010400000000800000008000000080000000800000fefefe",
            validity_error=[EOFException.INVALID_TYPE_SECTION_SIZE],
        ),
    ],
    ids=lambda c: c.name,
)
def test_invalid_containers(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Type section size should be 4 multiplied by the total number of code sections."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
