""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "76c94b69eccb06786fe0b95213ff209fa9aef7c1"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=[0xe3], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000e3",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_callf_truncated_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=[0xe3, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100020400000000800000e300",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_callf_truncated_1"
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
