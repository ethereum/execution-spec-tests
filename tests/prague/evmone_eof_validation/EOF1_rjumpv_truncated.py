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
                        0x05,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x60,
                        0x00,
                        0xe2,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000504000000008000006000e20000",
            EOFException.TRUNCATED_INSTRUCTION,
            id="EOF1_rjumpv_truncated_0",
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
                        0x07,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x60,
                        0x00,
                        0xe2,
                        0x01,
                        0x00,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000704000000008000006000e201000000",
            EOFException.TRUNCATED_INSTRUCTION,
            id="EOF1_rjumpv_truncated_1",
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
                        0x06,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x60,
                        0x02,
                        0xe2,
                        0x01,
                        0x00,
                        0x00,

                     ]),
            ),
            "0xef0001010004020001000604000000008000006002e2010000",
            EOFException.TRUNCATED_INSTRUCTION,
            id="EOF1_rjumpv_truncated_2",
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
                        0x09,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x60,
                        0x02,
                        0xe2,
                        0x02,
                        0x00,
                        0x00,
                        0x00,
                        0x03,
                        0xff,

                     ]),
            ),
            "0xef0001010004020001000904000000008000006002e20200000003ff",
            EOFException.TRUNCATED_INSTRUCTION,
            id="EOF1_rjumpv_truncated_3",
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
