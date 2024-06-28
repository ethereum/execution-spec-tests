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
                        0x09,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x01,
                        0x60,
                        0x00,
                        0xe2,
                        0x00,
                        0x00,
                        0x00,
                        0x60,
                        0x01,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000904000000008000016000e2000000600100",
            None,
            id="single_entry_case_0",
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
                        0x0e,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x01,
                        0x60,
                        0x00,
                        0xe2,
                        0x01,
                        0x00,
                        0x00,
                        0x00,
                        0x03,
                        0x60,
                        0x01,
                        0x00,
                        0x60,
                        0x02,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000e04000000008000016000e20100000003600100600200",
            None,
            id="two_entries_case_0",
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
                        0x0e,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x01,
                        0x60,
                        0x02,
                        0xe2,
                        0x01,
                        0x00,
                        0x00,
                        0x00,
                        0x03,
                        0x60,
                        0x01,
                        0x00,
                        0x60,
                        0x02,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000e04000000008000016002e20100000003600100600200",
            None,
            id="two_entries_case_2",
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
                        0x10,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x01,
                        0x60,
                        0x02,
                        0xe2,
                        0x02,
                        0x00,
                        0x00,
                        0x00,
                        0x03,
                        0xff,
                        0xf6,
                        0x60,
                        0x01,
                        0x00,
                        0x60,
                        0x02,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001001004000000008000016002e20200000003fff6600100600200",
            None,
            id="three_entries_case_2",
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
