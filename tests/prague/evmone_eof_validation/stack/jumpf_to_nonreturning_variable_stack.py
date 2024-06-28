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
                        0x0b,
                        0x00,
                        0x01,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x03,
                        0x05,
                        0x80,
                        0x00,
                        0x05,
                        0x5f,
                        0x60,
                        0x00,
                        0xe1,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0xe5,
                        0x00,
                        0x01,
                        0xfe,

                     ]),
            ),
            "0xef0001010008020002000b00010400000000800003058000055f6000e100025f5fe50001fe",
            EOFException.STACK_UNDERFLOW,
            id="jumpf_to_nonreturning_variable_stack_0",
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
                        0x0b,
                        0x00,
                        0x01,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x03,
                        0x03,
                        0x80,
                        0x00,
                        0x03,
                        0x5f,
                        0x60,
                        0x00,
                        0xe1,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0xe5,
                        0x00,
                        0x01,
                        0xfe,

                     ]),
            ),
            "0xef0001010008020002000b00010400000000800003038000035f6000e100025f5fe50001fe",
            EOFException.STACK_UNDERFLOW,
            id="jumpf_to_nonreturning_variable_stack_1",
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
                        0x08,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x0b,
                        0x00,
                        0x01,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x03,
                        0x01,
                        0x80,
                        0x00,
                        0x01,
                        0x5f,
                        0x60,
                        0x00,
                        0xe1,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0xe5,
                        0x00,
                        0x01,
                        0xfe,

                     ]),
            ),
            "0xef0001010008020002000b00010400000000800003018000015f6000e100025f5fe50001fe",
            None,
            id="jumpf_to_nonreturning_variable_stack_2",
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
                        0x08,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x0b,
                        0x00,
                        0x01,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x03,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x5f,
                        0x60,
                        0x00,
                        0xe1,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0xe5,
                        0x00,
                        0x01,
                        0xfe,

                     ]),
            ),
            "0xef0001010008020002000b00010400000000800003008000005f6000e100025f5fe50001fe",
            None,
            id="jumpf_to_nonreturning_variable_stack_3",
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
