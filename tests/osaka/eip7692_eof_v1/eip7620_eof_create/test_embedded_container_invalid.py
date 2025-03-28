"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"


# Too many subcontainers (257)
raw_container = Container(
    name="RAW_CONTAINER",
    raw_bytes=[
        0x00,  # Op.STOP
    ],
)

eof1_embedded_container_invalid_8 = Container(
    name="contract_with_invalid_container_8",
    sections=[Section.Code(code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP)]
    + [Section.Container(container=raw_container)] * 257,
    validity_error=[
        EOFException.TOO_MANY_CONTAINERS,
    ],
)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="contract_with_invalid_embedded_container_0",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                ]
            ),
            expected_bytecode="ef0001010004020001000603",
            validity_error=[EOFException.INCOMPLETE_SECTION_NUMBER],
        ),
        Container(
            name="contract_with_invalid_embedded_container_1",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                ]
            ),
            expected_bytecode="ef000101000402000100060300",
            validity_error=[EOFException.INCOMPLETE_SECTION_NUMBER],
        ),
        Container(
            name="contract_with_invalid_embedded_container_2",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x01,
                ]
            ),
            expected_bytecode="ef00010100040200010006030001",
            validity_error=[EOFException.MISSING_HEADERS_TERMINATOR],
        ),
        Container(
            name="contract_with_invalid_embedded_container_3",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x01,
                    0x00,
                ]
            ),
            expected_bytecode="ef0001010004020001000603000100",
            validity_error=[EOFException.INCOMPLETE_SECTION_SIZE],
        ),
        Container(
            name="contract_with_invalid_embedded_container_4",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    0x03,
                    0x00,
                    0x01,  # Container Sections (Length: 1)
                    0x00,
                    0x14,  #   Container Section 0 (Length: 20)
                    # --- Error: Invalid Data Header ---#
                ]
            ),
            expected_bytecode="ef000101000402000100060300010014",
            validity_error=[EOFException.MISSING_HEADERS_TERMINATOR],
        ),
        Container(
            name="contract_with_invalid_embedded_container_5",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x00,
                    0x04,
                    0x00,
                    0x00,
                    0x00,
                    0x00,
                    0x80,
                    0x00,
                    0x01,
                    0x60,
                    0x00,
                    0xE1,
                    0x00,
                    0x00,
                    0x00,
                ]
            ),
            expected_bytecode="ef0001010004020001000603000004000000008000016000e1000000",
            validity_error=[EOFException.ZERO_SECTION_SIZE],
        ),
        Container(
            name="contract_with_invalid_embedded_container_6",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Container(
                    container=Container(
                        name="EOFV1_0001",
                        raw_bytes=(
                            [
                                # --- Error: Empty code ---#
                            ]
                        ),
                    )
                ),
            ],
            expected_bytecode="ef00010100040200010006030001000004000000008000016000e1000000",
            validity_error=[EOFException.ZERO_SECTION_SIZE],
        ),
        Container(
            name="contract_with_invalid_embedded_container_7",
            raw_bytes=(
                [
                    0xEF,
                    0x00,
                    0x01,  # Version: 1
                    0x01,
                    0x00,
                    0x04,  # Types Length: 4
                    0x02,
                    0x00,
                    0x01,  # Code Sections (Length: 1)
                    0x00,
                    0x06,  #   Code Section 0 (Length: 6)
                    0x03,
                    0x00,
                    0x01,  # Container Sections (Length: 1)
                    0x00,
                    0x14,  #   Container Section 0 (Length: 20)
                    0x04,
                    0x00,
                    0x00,  # Data Length: 0
                    0x00,  # Terminator
                    # Code Section 0 types
                    0x00,  #   Inputs: 0
                    0x80,  #   Outputs: 0 (Non-returning function)
                    0x00,
                    0x01,  #   Max Stack Height: 1
                    # Code Section 0
                    0x60,
                    0x00,  #  [0] PUSH1(0)
                    0xE1,
                    0x00,
                    0x00,  #  [2] RJUMPI(0)
                    0x00,  #  [5] STOP
                    # --- Error: Invalid Container Content ---#
                ]
            ),
            expected_bytecode="ef00010100040200010006030001001404000000008000016000e1000000",
            validity_error=[EOFException.INVALID_SECTION_BODIES_SIZE],
        ),
        eof1_embedded_container_invalid_8,
    ],
    ids=lambda c: c.name,
)
def test_embedded_container_invalid(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contract with invalid subcontainers headers or contents."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
