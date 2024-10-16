""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4200.md"
REFERENCE_SPEC_VERSION = "b452cf8a47e5b5bf08a1576a4dfaf828306beb5a"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=[0x60, 0x00, 0xe2, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006000e20000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_rjumpv_truncated_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=[0x60, 0x00, 0xe2, 0x01, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006000e201000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_rjumpv_truncated_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=[0x60, 0x02, 0xe2, 0x01, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006002e2010000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_rjumpv_truncated_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=[0x60, 0x02, 0xe2, 0x02, 0x00, 0x00, 0x00, 0x03, 0xff], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006002e20200000003ff",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_rjumpv_truncated_3"
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
