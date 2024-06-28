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
                        0x04,
                        0x00,
                        0x03,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x02,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0x5f,
                        0xe4,

                     ]),
            ),
            "0xef000101000802000200040003040000000080000200020002e30001005f5fe4",
            None,
            id="retf_stack_validation_0",
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
                        0x04,
                        0x00,
                        0x02,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x01,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0xe4,

                     ]),
            ),
            "0xef000101000802000200040002040000000080000200020001e30001005fe4",
            EOFException.STACK_UNDERFLOW,
            id="retf_stack_validation_1",
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
                        0x04,
                        0x00,
                        0x04,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x03,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe4,

                     ]),
            ),
            "0xef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
            EOFException.STACK_HIGHER_THAN_OUTPUTS,
            id="retf_stack_validation_2",
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
                        0x05,
                        0x00,
                        0x0d,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x02,
                        0x01,
                        0x02,
                        0x00,
                        0x02,
                        0x5f,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0xe1,
                        0x00,
                        0x07,
                        0x60,
                        0x01,
                        0x60,
                        0x01,
                        0xe0,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0xe4,

                     ]),
            ),
            "0xef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
            None,
            id="retf_stack_validation_3",
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
