""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "9c7c91bf7b9b7af9e76248f7921a03ddc17f99ef"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.ADD + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000000100",
              EOFException.STACK_UNDERFLOW,
              id="underflow_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000802000200040002040000000080000101020002e30001005fe4",
              EOFException.STACK_UNDERFLOW,
              id="underflow_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.JUMPF[2], code_outputs=2, max_stack_height=0),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040003000204000000008000020002000001020002e3000100e500025fe4",
              EOFException.STACK_UNDERFLOW,
              id="underflow_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, code_inputs=1, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200030005040000000080000001800003e5000160006000fd",
              EOFException.STACK_UNDERFLOW,
              id="underflow_3"
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
