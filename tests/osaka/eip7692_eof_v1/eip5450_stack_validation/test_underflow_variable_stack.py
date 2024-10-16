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
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.LOG2 + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000035f6000e100025f5fa200",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.ADD + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000035f6000e100025f5f0100",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.CALLF[1] + Op.STOP, max_stack_height=4),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=4, code_outputs=5, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010008020002000c00020400000000800004040500055f6000e100025f5fe30001005fe4",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.CALLF[1] + Op.STOP, max_stack_height=4),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=3, code_outputs=4, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010008020002000c00020400000000800004030400045f6000e100025f5fe30001005fe4",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2], code_outputs=3, max_stack_height=3),
                    Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=5, code_outputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c0200030004000b000304000000008000030003000305030003e30001005f6000e100025f5fe500025050e4",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, code_inputs=5, max_stack_height=7),
                    ],
              )
              ,
              "ef0001010008020002000b00050400000000800000058000075f6000e100025f5fe5000160006000fd",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, code_inputs=3, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010008020002000b00050400000000800000038000055f6000e100025f5fe5000160006000fd",
              EOFException.STACK_UNDERFLOW,
              id="underflow_variable_stack_6"
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
