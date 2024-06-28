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
                        0x0c,
                        0x02,
                        0x00,
                        0x03,
                        0x00,
                        0x04,
                        0x00,
                        0x06,
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
                        0x00,
                        0x01,
                        0x00,
                        0x02,
                        0x02,
                        0x01,
                        0x00,
                        0x02,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0x5f,
                        0xe3,
                        0x00,
                        0x02,
                        0xe4,
                        0x50,
                        0xe4,

                     ]),
            ),
            "0xef000101000c02000300040006000204000000008000010001000202010002e30001005f5fe30002e450e4",
            None,
            id="callf_stack_validation_0",
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
                        0x0c,
                        0x02,
                        0x00,
                        0x03,
                        0x00,
                        0x04,
                        0x00,
                        0x07,
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
                        0x00,
                        0x01,
                        0x00,
                        0x03,
                        0x02,
                        0x01,
                        0x00,
                        0x02,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe3,
                        0x00,
                        0x02,
                        0xe4,
                        0x50,
                        0xe4,

                     ]),
            ),
            "0xef000101000c02000300040007000204000000008000010001000302010002e30001005f5f5fe30002e450e4",
            EOFException.STACK_HIGHER_THAN_OUTPUTS,
            id="callf_stack_validation_1",
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
                        0x0c,
                        0x02,
                        0x00,
                        0x03,
                        0x00,
                        0x04,
                        0x00,
                        0x05,
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
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x02,
                        0x01,
                        0x00,
                        0x02,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0xe3,
                        0x00,
                        0x02,
                        0xe4,
                        0x50,
                        0xe4,

                     ]),
            ),
            "0xef000101000c02000300040005000204000000008000010001000102010002e30001005fe30002e450e4",
            EOFException.STACK_UNDERFLOW,
            id="callf_stack_validation_2",
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
