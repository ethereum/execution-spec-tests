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
                  name="EOFV1_0002",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x01,
                          0x00,
                          0x04,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x03,
                          0x04,
                          0x00,
                          0x00,
                          0x00,
                          0x00,
                          0x01,
                          0x00,
                          0x00,
                          0x60,
                          0x00,
                          0x5c,
                      ]),
              ),
              "ef00010100040200010003040000000001000060005c",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x01,
                          0x00,
                          0x04,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x04,
                          0x00,
                          0x00,
                          0x00,
                          0x01,
                          0x80,
                          0x00,
                          0x00,
                          0xfe,
                      ]),
              ),
              "ef000101000402000100010400000001800000fe",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_2"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x01,
                          0x00,
                          0x04,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x03,
                          0x04,
                          0x00,
                          0x00,
                          0x00,
                          0x02,
                          0x03,
                          0x00,
                          0x00,
                          0x60,
                          0x00,
                          0x5c,
                      ]),
              ),
              "ef00010100040200010003040000000203000060005c",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_3"
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
