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
                        0x02,

                     ]),
            ),
            "0xef0002",
            EOFException.INVALID_VERSION,
            id="validate_EOF_version_0",
        ),
        pytest.param(
            Container(
                name="EOF1V00002",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0xff,

                     ]),
            ),
            "0xef00ff",
            EOFException.INVALID_VERSION,
            id="validate_EOF_version_1",
        ),
        pytest.param(
            Container(
                name="EOF1V00003",
                raw_bytes=bytes(
                     [
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
                        0x02,
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
            ),
            "0xef000001000402000100030200040000800000600000aabbccdd",
            EOFException.INVALID_VERSION,
            id="valid_except_version_00",
        ),
        pytest.param(
            Container(
                name="EOF1V00004",
                raw_bytes=bytes(
                     [
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
                        0x02,
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
            ),
            "0xef000201000402000100030200040000800000600000aabbccdd",
            EOFException.INVALID_VERSION,
            id="valid_except_version_02",
        ),
        pytest.param(
            Container(
                name="EOF1V00005",
                raw_bytes=bytes(
                     [
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
                        0x02,
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
            ),
            "0xef00ff01000402000100030200040000800000600000aabbccdd",
            EOFException.INVALID_VERSION,
            id="valid_except_version_FF",
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
