"""
EOF v1 validation code
"""

import pytest
from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools.eof.v1 import Container, EOFException

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
            Container(
                name="EOF1V00001",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x08,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xfe,
                        0xfe,

                     ]),
            ),
            "0xef000101000802000200010001000080000000800000fefe",
            EOFException.MISSING_DATA_SECTION,
            id="no_data_section",
        ),
        pytest.param(
            Container(
                name="EOF1V00002",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x08,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x03,
                        0x00,
                        0x01,
                        0x04,
                        0x00,
                        0x01,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xe5,
                        0x00,
                        0x01,
                        0xfe,
                        0xda,

                     ]),
            ),
            "0xef000101000802000200030001040001000080000000800000e50001feda",
            None,
            id="with_data_section",
        ),
        pytest.param(
            Container(
                name="EOF1V00003",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x10,
                        0x02,
                        0x00,
                        0x04,
                        0x00,
                        0x05,
                        0x00,
                        0x06,
                        0x00,
                        0x08,
                        0x00,
                        0x02,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x00,
                        0x03,
                        0x02,
                        0x03,
                        0x00,
                        0x03,
                        0x5f,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x50,
                        0xe3,
                        0x00,
                        0x02,
                        0x50,
                        0xe4,
                        0x30,
                        0x80,
                        0xe3,
                        0x00,
                        0x03,
                        0x50,
                        0x50,
                        0xe4,
                        0x80,
                        0xe4,

                     ]),
            ),
            "0xef0001010010020004000500060008000204000000008000010100000100010003020300035fe300010050e3000250e43080e300035050e480e4",
            None,
            id="non_void_input_output",
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
    if expected_hex_bytecode[0:2] == "0x":
        expected_hex_bytecode = expected_hex_bytecode[2:]
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
