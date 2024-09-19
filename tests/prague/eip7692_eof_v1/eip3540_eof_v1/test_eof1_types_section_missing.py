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
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x00,
                          0xfe,
                      ]),
              ),
              "ef0001020001000100fe",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_types_section_missing_1"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0003",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x03,
                          0x00,
                          0x01,
                          0x00,
                          0xfe,
                          0xda,
                      ]),
              ),
              "ef0001020001000103000100feda",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_types_section_missing_2"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0004",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x04,
                          0x00,
                          0x01,
                          0x00,
                          0xfe,
                          0xda,
                      ]),
              ),
              "ef0001020001000104000100feda",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_types_section_missing_3"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0005",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x02,
                          0x00,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x00,
                          0xfe,
                          0xfe,
                      ]),
              ),
              "ef00010200020001000100fefe",
              EOFException.MISSING_TYPE_HEADER,
              id="eof1_types_section_missing_4"
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
