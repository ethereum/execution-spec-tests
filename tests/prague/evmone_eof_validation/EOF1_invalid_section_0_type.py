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
                        0x00,
                        0x00,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef00010100040200010001040000000000000000",
            EOFException.INVALID_FIRST_SECTION_TYPE,
            id="EOF1_invalid_section_0_type_0",
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
            "0xef00010100040200010003040000000001000060005c",
            EOFException.INVALID_FIRST_SECTION_TYPE,
            id="EOF1_invalid_section_0_type_1",
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
            "0xef000101000402000100010400000001800000fe",
            EOFException.INVALID_FIRST_SECTION_TYPE,
            id="EOF1_invalid_section_0_type_2",
        ),
        pytest.param(
            Container(
                name="EOF1V00004",
                raw_bytes=bytes(
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
            "0xef00010100040200010003040000000203000060005c",
            EOFException.INVALID_FIRST_SECTION_TYPE,
            id="EOF1_invalid_section_0_type_3",
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
