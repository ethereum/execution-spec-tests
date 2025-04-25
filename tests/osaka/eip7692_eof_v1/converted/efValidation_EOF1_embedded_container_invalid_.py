import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="EOF1_embedded_container_invalid_0",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                ]
            ),
            validity_error=EOFException.INCOMPLETE_SECTION_NUMBER,
        ),
        Container(
            name="EOF1_embedded_container_invalid_1",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                ]
            ),
            validity_error=EOFException.INCOMPLETE_SECTION_NUMBER,
        ),
        Container(
            name="EOF1_embedded_container_invalid_2",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x01,
                ]
            ),
            validity_error=EOFException.MISSING_HEADERS_TERMINATOR,
        ),
        Container(
            name="EOF1_embedded_container_invalid_3",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x01,
                    0x00,
                ]
            ),
            validity_error=EOFException.INCOMPLETE_SECTION_SIZE,
        ),
        Container(
            name="EOF1_embedded_container_invalid_4",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    0x03, 0x00, 0x01, # Container Sections (Length: 1)
                          0x00, 0x00,
                          0x00, 0x14, #   Container Section 0 (Length: 20)
                    # --- Error: Invalid Data Header ---#
                ]
            ),
            validity_error=EOFException.MISSING_HEADERS_TERMINATOR,
        ),
        Container(
            name="EOF1_embedded_container_invalid_5",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    # --- Error: Invalid Container Header ---#
                    0x03,
                    0x00,
                    0x00,
                    0xFF,
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
            validity_error=EOFException.ZERO_SECTION_SIZE,
        ),
        Container(
            name="EOF1_embedded_container_invalid_6",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Container(
                    container=Container(
                        name="EOFV1_0001",
                        raw_bytes=([]), # Empty subcontainer
                    )
                ),
            ],
            validity_error=EOFException.ZERO_SECTION_SIZE,
        ),
        Container(
            name="EOF1_embedded_container_invalid_7",
            raw_bytes=(
                [
                    0xEF, 0x00, 0x01, # Version: 1
                    0x01, 0x00, 0x04, # Types Length: 4
                    0x02, 0x00, 0x01, # Code Sections (Length: 1)
                          0x00, 0x06, #   Code Section 0 (Length: 6)
                    0x03, 0x00, 0x01, # Container Sections (Length: 1)
                          0x00, 0x00,
                          0x00, 0x14, #   Container Section 0 (Length: 20)
                    0xFF, 0x00, 0x00, # Data Length: 0
                                0x00, # Terminator
                                      # Code Section 0 types
                                0x00, #   Inputs: 0
                                0x80, #   Outputs: 0 (Non-returning function)
                          0x00, 0x01, #   Max Stack Height: 1
                                      # Code Section 0
                           0x60,0x00, #  [0] PUSH1(0)
                      0xE1,0x00,0x00, #  [2] RJUMPI(0)
                                0x00, #  [5] STOP
                    # --- Error: Invalid Container Content ---#
                ]
            ),
            validity_error=EOFException.INVALID_SECTION_BODIES_SIZE,
        ),
        Container(
            name="EOF1_embedded_container_invalid_8",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP,
                    max_stack_height=1,
                ),
            ] + [
                Section.Container(
                    container=Container(
                        raw_bytes=([0x00]),
                    )
                ),
            ] * 257,
            validity_error=EOFException.TOO_MANY_CONTAINERS,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
