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
                        0x02,
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x04,
                        0x00,
                        0xfe,
                        0x00,
                        0x80,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef0001020001000101000400fe00800000",
            EOFException.MISSING_TYPE_HEADER,
            id="EOF1_type_section_not_first_0",
        ),
        pytest.param(
            Container(
                name="EOF1V00002",
                raw_bytes=bytes(
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
                        0x01,
                        0x00,
                        0x04,
                        0x00,
                        0xfe,
                        0xfe,
                        0x00,
                        0x80,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef00010200020001000101000400fefe00800000",
            EOFException.MISSING_TYPE_HEADER,
            id="EOF1_type_section_not_first_1",
        ),
        pytest.param(
            Container(
                name="EOF1V00003",
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,
                        0x02,
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x04,
                        0x04,
                        0x00,
                        0x03,
                        0x00,
                        0xfe,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xaa,
                        0xbb,
                        0xcc,

                     ]),
            ),
            "0xef0001020001000101000404000300fe00800000aabbcc",
            EOFException.MISSING_TYPE_HEADER,
            id="EOF1_type_section_not_first_2",
        ),
        pytest.param(
            Container(
                name="EOF1V00004",
                raw_bytes=bytes(
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
                        0x03,
                        0x01,
                        0x00,
                        0x04,
                        0x00,
                        0xfe,
                        0xaa,
                        0xbb,
                        0xcc,
                        0x00,
                        0x80,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef0001020001000104000301000400feaabbcc00800000",
            EOFException.MISSING_TYPE_HEADER,
            id="EOF1_type_section_not_first_3",
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
