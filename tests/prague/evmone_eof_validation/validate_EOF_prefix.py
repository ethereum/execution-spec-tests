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
                        0x00,

                     ]),
            ),
            "0x00",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_0",
        ),
        pytest.param(
            Container(
                name="EOF1V00002",
                raw_bytes=bytes(
                     [
                        0xfe,

                     ]),
            ),
            "0xfe",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_1",
        ),
        pytest.param(
            Container(
                name="EOF1V00003",
                raw_bytes=bytes(
                     [
                        0xef,

                     ]),
            ),
            "0xef",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_2",
        ),
        pytest.param(
            Container(
                name="EOF1V00004",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x01,
                        0x01,

                     ]),
            ),
            "0xef0101",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_3",
        ),
        pytest.param(
            Container(
                name="EOF1V00005",
                raw_bytes=bytes(
                     [
                        0xef,
                        0xef,
                        0x01,

                     ]),
            ),
            "0xefef01",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_4",
        ),
        pytest.param(
            Container(
                name="EOF1V00006",
                raw_bytes=bytes(
                     [
                        0xef,
                        0xff,
                        0x01,

                     ]),
            ),
            "0xefff01",
            EOFException.INVALID_MAGIC,
            id="validate_EOF_prefix_5",
        ),
        pytest.param(
            Container(
                name="EOF1V00007",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,

                     ]),
            ),
            "0xef00",
            EOFException.INVALID_VERSION,
            id="validate_EOF_prefix_6",
        ),
        pytest.param(
            Container(
                name="EOF1V00008",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,

                     ]),
            ),
            "0xef0001",
            EOFException.MISSING_HEADERS_TERMINATOR,
            id="validate_EOF_prefix_7",
        ),
        pytest.param(
            Container(
                name="EOF1V00009",
                raw_bytes=bytes(
                     [
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
                        0x03,
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
            "0xefff0101000402000100030300040000800000600000aabbccdd",
            EOFException.INVALID_MAGIC,
            id="valid_except_magic",
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
