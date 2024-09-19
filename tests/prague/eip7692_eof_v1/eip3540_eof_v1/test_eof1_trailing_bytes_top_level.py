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
                          0x00,
                          0x80,
                          0x00,
                          0x00,
                          0xfe,
                          0xde,
                          0xad,
                          0xbe,
                          0xef,
                      ]),
              ),
              "ef000101000402000100010400000000800000fedeadbeef",
              EOFException.INVALID_SECTION_BODIES_SIZE,
              id="eof1_trailing_bytes_top_level_0"
        ),
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
                          0x01,
                          0x04,
                          0x00,
                          0x02,
                          0x00,
                          0x00,
                          0x80,
                          0x00,
                          0x00,
                          0xfe,
                          0xaa,
                          0xbb,
                          0xde,
                          0xad,
                          0xbe,
                          0xef,
                      ]),
              ),
              "ef000101000402000100010400020000800000feaabbdeadbeef",
              EOFException.INVALID_SECTION_BODIES_SIZE,
              id="eof1_trailing_bytes_top_level_1"
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
