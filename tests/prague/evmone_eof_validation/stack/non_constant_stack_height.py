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
                        0x0e,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x04,
                        0x5f,
                        0xe1,
                        0x00,
                        0x07,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe1,
                        0x00,
                        0x01,
                        0x50,
                        0x5f,
                        0x5f,
                        0xfd,

                     ]),
            ),
            "0xef0001010004020001000e04000000008000045fe100075f5f5fe10001505f5ffd",
            None,
            id="non_constant_stack_height_0",
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
                        0x0f,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x05,
                        0x5f,
                        0x5f,
                        0xe1,
                        0x00,
                        0x07,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe1,
                        0x00,
                        0x01,
                        0x50,
                        0x5f,
                        0x5f,
                        0xfd,

                     ]),
            ),
            "0xef0001010004020001000f04000000008000055f5fe100075f5f5fe10001505f5ffd",
            None,
            id="non_constant_stack_height_1",
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
                        0x0f,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x04,
                        0x5f,
                        0xe1,
                        0x00,
                        0x07,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe1,
                        0x00,
                        0x01,
                        0x50,
                        0x50,
                        0x5f,
                        0x5f,
                        0xfd,

                     ]),
            ),
            "0xef0001010004020001000f04000000008000045fe100075f5f5fe1000150505f5ffd",
            EOFException.STACK_UNDERFLOW,
            id="non_constant_stack_height_2",
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
