""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "7a664ec21843615efde4dae03205758f6569cdb7"

# Too many subcontainers (257)
raw_container = Container(
    name="RAW_CONTAINER",
    raw_bytes=[
        0x00,   # Op.STOP
    ]
)

eof1_embedded_container_invalid_8 = Container(
    name="EOFV1_0009",
    sections = [Section.Code(code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP)] 
        + [Section.Container(container=raw_container)] * 257 
)


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                  name="EOFV1_0001",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      #--- Error: Invalid Container Header ---#
                      0x03,
                    ]),
              )
              ,
              "ef0001010004020001000603",
              EOFException.INCOMPLETE_SECTION_NUMBER,
              id="eof1_embedded_container_invalid_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      #--- Error: Invalid Container Header ---#
                      0x03,
                      0x00,
                    ]),
              )
              ,
              "ef000101000402000100060300",
              EOFException.INCOMPLETE_SECTION_NUMBER,
              id="eof1_embedded_container_invalid_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      #--- Error: Invalid Container Header ---#
                      0x03,
                      0x00,
                      0x01,
                    ]),
              )
              ,
              "ef00010100040200010006030001",
              EOFException.MISSING_HEADERS_TERMINATOR,
              id="eof1_embedded_container_invalid_2"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      #--- Error: Invalid Container Header ---#
                      0x03,
                      0x00,
                      0x01,
                      0x00,
                    ]),
              )
              ,
              "ef0001010004020001000603000100",
              EOFException.INCOMPLETE_SECTION_SIZE,
              id="eof1_embedded_container_invalid_3"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      0x03, 0x00, 0x01, # Container Sections (Length: 1)
                            0x00, 0x14, #   Container Section 0 (Length: 20)
                      #--- Error: Invalid Data Header ---#
                      
                    ]),
              )
              ,
              "ef000101000402000100060300010014",
              EOFException.MISSING_HEADERS_TERMINATOR,
              id="eof1_embedded_container_invalid_4"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0006",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      #--- Error: Invalid Container Header ---#
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
                      0xe1,
                      0x00,
                      0x00,
                      0x00,
                    ]),
              )
              ,
              "ef0001010004020001000603000004000000008000016000e1000000",
              EOFException.ZERO_SECTION_SIZE,
              id="eof1_embedded_container_invalid_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPI[0] + Op.STOP, max_stack_height=1),
                    Section.Container(
                         container=Container(
                             name="EOFV1_0001",
                             raw_bytes=(
                               [
                                 #--- Error found: Empty code ---#
                                 
                               ]),
                         )
                     ),
              					      
                ],
              )
              ,
              "ef00010100040200010006030001000004000000008000016000e1000000",
              EOFException.ZERO_SECTION_SIZE,
              id="eof1_embedded_container_invalid_6"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0008",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x04, # Types Length: 4
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x06, #   Code Section 0 (Length: 6)
                      0x03, 0x00, 0x01, # Container Sections (Length: 1)
                            0x00, 0x14, #   Container Section 0 (Length: 20)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                                        # Code Section 0 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x01, #   Max Stack Height: 1
                      
                                        # Code Section 0
                            0x60, 0x00, #  [0] PUSH1(0) 
                      0xe1, 0x00, 0x00, #  [2] RJUMPI(0) 
                                  0x00, #  [5] STOP 
                      #--- Error: Invalid Container Content ---#
                      
                    ]),
              )
              ,
              "ef00010100040200010006030001001404000000008000016000e1000000",
              EOFException.INVALID_SECTION_BODIES_SIZE,
              id="eof1_embedded_container_invalid_7"
        ),
        pytest.param(
              eof1_embedded_container_invalid_8,
              "ef000101000402000100060301010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000100010001000104000000008000016000e10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
              EOFException.TOO_MANY_CONTAINER_SECTIONS,
              id="eof1_embedded_container_invalid_8"
        ),
        
    ]
)

def test_example_valid_invalid(
    eof_test: EOFTestFiller,
    eof_code: Container,
    expected_hex_bytecode: str,
    exception: EOFException | None,
):
    """
    Verify eof container construction and exception
    """
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
