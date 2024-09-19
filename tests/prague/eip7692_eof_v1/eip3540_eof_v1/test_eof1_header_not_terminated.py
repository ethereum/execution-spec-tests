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
                  name="EOFV1_0006",
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
                          0x01,
                      ]),
              ),
              "ef00010100040200010001040001",
              EOFException.MISSING_HEADERS_TERMINATOR,
              id="eof1_header_not_terminated_5"
        ),
        pytest.param(
              Container(
                  name="EOFV1_0007",
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
                          0x01,
                          0xfe,
                          0xaa,
                      ]),
              ),
              "ef00010100040200010001040001feaa",
              EOFException.MISSING_TERMINATOR,
              id="eof1_header_not_terminated_6"
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
