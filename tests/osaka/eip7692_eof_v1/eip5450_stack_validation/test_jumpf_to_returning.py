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
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.JUMPF[2], code_outputs=2, max_stack_height=0),
                    Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040003000304000000008000020002000000020002e3000100e500025f5fe4",
              None,
              id="jumpf_to_returning_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[2], code_outputs=2, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040005000304000000008000020002000200020002e30001005f5fe500025f5fe4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="jumpf_to_returning_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[2], code_outputs=2, max_stack_height=3),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040006000204000000008000020002000303020003e30001005f5f5fe5000250e4",
              None,
              id="jumpf_to_returning_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[2], code_outputs=2, max_stack_height=4),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040007000204000000008000020002000403020003e30001005f5f5f5fe5000250e4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="jumpf_to_returning_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[2], code_outputs=2, max_stack_height=2),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040005000204000000008000020002000203020003e30001005f5fe5000250e4",
              EOFException.STACK_UNDERFLOW,
              id="jumpf_to_returning_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 + Op.JUMPF[2], code_outputs=2, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000c02000300040004000204000000008000020002000100010001e30001005fe500025fe4",
              None,
              id="jumpf_to_returning_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[2], code_outputs=2, max_stack_height=3),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000c02000300040006000204000000008000020002000300010001e30001005f5f5fe500025fe4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="jumpf_to_returning_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.JUMPF[2], code_outputs=2, max_stack_height=0),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000c02000300040003000204000000008000020002000000010001e3000100e500025fe4",
              EOFException.STACK_UNDERFLOW,
              id="jumpf_to_returning_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[2], code_outputs=2, max_stack_height=4),
                    Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040007000304000000008000020002000403010003e30001005f5f5f5fe500025050e4",
              None,
              id="jumpf_to_returning_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 5 + Op.JUMPF[2], code_outputs=2, max_stack_height=5),
                    Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040008000304000000008000020002000503010003e30001005f5f5f5f5fe500025050e4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="jumpf_to_returning_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[2], code_outputs=2, max_stack_height=3),
                    Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040006000304000000008000020002000303010003e30001005f5f5fe500025050e4",
              EOFException.STACK_UNDERFLOW,
              id="jumpf_to_returning_10"
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
