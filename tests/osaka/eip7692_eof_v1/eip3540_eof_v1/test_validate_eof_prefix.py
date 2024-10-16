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
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0xff,
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
                      0x04,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0x60,
                      0x00,
                      0x00,
                      0xaa,
                      0xbb,
                      0xcc,
                      0xdd,
                    ]),
              )
              ,
              "efff0101000402000100030400040000800000600000aabbccdd",
              EOFException.INVALID_MAGIC,
              id="valid_except_magic"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0x00,
                    ]),
              )
              ,
              "00",
              EOFException.INVALID_MAGIC,
              id="validate_eof_prefix_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xfe,
                    ]),
              )
              ,
              "fe",
              EOFException.INVALID_MAGIC,
              id="validate_eof_prefix_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0x01,
                      0x01,
                    ]),
              )
              ,
              "ef0101",
              EOFException.INVALID_MAGIC,
              id="validate_eof_prefix_3"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0006",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0xef,
                      0x01,
                    ]),
              )
              ,
              "efef01",
              EOFException.INVALID_MAGIC,
              id="validate_eof_prefix_4"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0007",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0xff,
                      0x01,
                    ]),
              )
              ,
              "efff01",
              EOFException.INVALID_MAGIC,
              id="validate_eof_prefix_5"
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
