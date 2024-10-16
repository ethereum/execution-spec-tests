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
                      0x01, 0x00, 0x00, # Types Length: 0
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                      0x04, 0x00, 0x00, # Data Length: 0
                                  0x00, # Terminator
                      #--- Error: Code and Type sections mismatch ---#
                                        # Code Section 0
                                  0xfe, #  [0] INVALID 
                    ]),
              )
              ,
              "ef0001010000020001000104000000fe",
              EOFException.ZERO_SECTION_SIZE,
              id="eof1_types_section_0_size_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x00, # Types Length: 0
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                      0x04, 0x00, 0x01, # Data Length: 1
                                  0x00, # Terminator
                      #--- Error: Code and Type sections mismatch ---#
                                        # Code Section 0
                                  0xfe, #  [0] INVALID 
                                        # Data Section
                      0xda,
                    ]),
              )
              ,
              "ef0001010000020001000104000100feda",
              EOFException.ZERO_SECTION_SIZE,
              id="eof1_types_section_0_size_1"
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
