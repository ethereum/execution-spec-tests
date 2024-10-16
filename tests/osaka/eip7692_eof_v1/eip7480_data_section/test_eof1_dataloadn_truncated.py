""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7480.md"
REFERENCE_SPEC_VERSION = "d1cafe61fa83c0f2a752bb0aaf220cd0d20bca98"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=[0xd1], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000d1",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_dataloadn_truncated_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=[0xd1, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100020400000000800000d100",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_dataloadn_truncated_1"
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
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
