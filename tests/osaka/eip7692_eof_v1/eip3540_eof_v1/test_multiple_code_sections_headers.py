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
                      0x01, 0x00, 0x08, # Types Length: 8
                      0x02, 0x00, 0x01, # Code Sections (Length: 1)
                            0x00, 0x04, #   Code Section 0 (Length: 4)
                      #--- Error: Invalid Data Header ---#
                      0x02,
                      0x00,
                      0x01,
                      0x00,
                      0x05,
                      0x04,
                      0x00,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0x04,
                      0x5c,
                      0x00,
                      0x00,
                      0x00,
                      0x40,
                      0x5c,
                      0x00,
                      0x00,
                      0x00,
                      0x2e,
                      0x00,
                      0x05,
                    ]),
              )
              ,
              "ef0001010008020001000402000100050400000000800000045c000000405c0000002e0005",
              EOFException.MISSING_DATA_SECTION,
              id="multiple_code_sections_headers_0"
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
