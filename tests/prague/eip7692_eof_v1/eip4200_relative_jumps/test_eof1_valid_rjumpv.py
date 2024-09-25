""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
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
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[0] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e2000000600100",
              None,
              id="single_entry_case_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[0,3] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000016000e20100000003600100600200",
              None,
              id="two_entries_case_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,-10] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e20200000003fff6600100600200",
              None,
              id="three_entries_case_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000016002e20100000003600100600200",
              None,
              id="two_entries_case_2"
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
