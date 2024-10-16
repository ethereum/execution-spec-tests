""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
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
                      0x00,
                      0xff,
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
              "ef00ff01000402000100030400040000800000600000aabbccdd",
              EOFException.INVALID_VERSION,
              id="valid_except_version_ff"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0002",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0x00,
                      0x00,
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
              "ef000001000402000100030400040000800000600000aabbccdd",
              EOFException.INVALID_VERSION,
              id="valid_except_version_00"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0x00,
                      0x02,
                    ]),
              )
              ,
              "ef0002",
              EOFException.INVALID_VERSION,
              id="validate_eof_version_0"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0x00,
                      0xff,
                    ]),
              )
              ,
              "ef00ff",
              EOFException.INVALID_VERSION,
              id="validate_eof_version_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                    [
                      #--- Error found: Invalid Magic+Version ---#
                      0xef,
                      0x00,
                      0x02,
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
              "ef000201000402000100030400040000800000600000aabbccdd",
              EOFException.INVALID_VERSION,
              id="valid_except_version_02"
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
