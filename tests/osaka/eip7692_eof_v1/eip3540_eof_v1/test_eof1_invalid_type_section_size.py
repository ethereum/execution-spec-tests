""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "12ca2f0bd2f7380100e154aaaa0995c46cbb2710"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                  name="EOFV1_0001",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x01, # Types Length: 1
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                      #--- Error: Invalid Types Content ---#
                      0x00,
                      0xfe,
                    ]),
              )
              ,
              "ef000101000102000100010400000000fe",
              EOFException.INVALID_TYPE_SECTION_SIZE,
              id="eof1_invalid_type_section_size_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x02, # Types Length: 2
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                      #--- Error: Invalid Types Content ---#
                      0x00,
                      0x80,
                      0xfe,
                    ]),
              )
              ,
              "ef00010100020200010001040000000080fe",
              EOFException.INVALID_TYPE_SECTION_SIZE,
              id="eof1_invalid_type_section_size_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x08, # Types Length: 8
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                                        # Code Section 0 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                                        # Code Section 1 types
                                  0x00, #   Inputs: 0
                                  0x00, #   Outputs: 0
                            0x00, 0x00, #   Max Stack Height: 0
                      #--- Error: Code and Type sections mismatch ---#
                                        # Code Section 0
                                  0xfe, #  [0] INVALID 
                    ]),
              )
              ,
              "ef00010100080200010001040000000080000000000000fe",
              EOFException.INVALID_TYPE_SECTION_SIZE,
              id="eof1_invalid_type_section_size_2"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x08, # Types Length: 8
                      0x02, 0x00, 0x03, # Code Sections (Length: 3)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                            0x00, 0x01, #   Code Section 1 (Length: 1)
                            0x00, 0x01, #   Code Section 2 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                                        # Code Section 0 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                                        # Code Section 1 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                      #--- Error: Code and Type sections mismatch ---#
                                        # Code Section 0
                                  0xfe, #  [0] INVALID 
                                        # Code Section 1
                                  0xfe, #  [0] INVALID 
                                        # Code Section 2
                                  0xfe, #  [0] INVALID 
                    ]),
              )
              ,
              "ef0001010008020003000100010001040000000080000000800000fefefe",
              EOFException.INVALID_TYPE_SECTION_SIZE,
              id="eof1_invalid_type_section_size_3"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x10, # Types Length: 16
                      0x02, 0x00, 0x03, # Code Sections (Length: 3)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                            0x00, 0x01, #   Code Section 1 (Length: 1)
                            0x00, 0x01, #   Code Section 2 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                                        # Code Section 0 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                                        # Code Section 1 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                                        # Code Section 2 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                                        # Code Section 3 types
                                  0x00, #   Inputs: 0
                                  0x80, #   Outputs: 0 (Non-returning function)
                            0x00, 0x00, #   Max Stack Height: 0
                      #--- Error: Code and Type sections mismatch ---#
                                        # Code Section 0
                                  0xfe, #  [0] INVALID 
                                        # Code Section 1
                                  0xfe, #  [0] INVALID 
                                        # Code Section 2
                                  0xfe, #  [0] INVALID 
                    ]),
              )
              ,
              "ef00010100100200030001000100010400000000800000008000000080000000800000fefefe",
              EOFException.INVALID_TYPE_SECTION_SIZE,
              id="eof1_invalid_type_section_size_4"
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
