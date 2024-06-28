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
                        0x05,
                        0x00,
                        0x04,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x03,
                        0x00,
                        0x03,
                        0x00,
                        0x02,
                        0x00,
                        0x05,
                        0x00,
                        0x03,
                        0xe3,
                        0x00,
                        0x01,
                        0x00,
                        0xe5,
                        0x00,
                        0x02,
                        0x5f,
                        0x5f,
                        0x5f,
                        0x5f,
                        0x5f,
                        0xe4,

                     ]),
            ),
            "0xef000101000c02000300040005000404000000008000030003000200050003e3000100e500025f5f5f5f5fe4",
            EOFException.JUMPF_DESTINATION_INCOMPATIBLE_OUTPUTS,
            id="jumpf_incompatible_outputs_0",
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
