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
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 * 2 + Op.CALLF[2] + Op.RETF, code_outputs=1, max_stack_height=2),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040006000204000000008000010001000202010002e30001005f5fe30002e450e4",
              None,
              id="callf_stack_validation_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 * 3 + Op.CALLF[2] + Op.RETF, code_outputs=1, max_stack_height=3),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040007000204000000008000010001000302010002e30001005f5f5fe30002e450e4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="callf_stack_validation_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 + Op.CALLF[2] + Op.RETF, code_outputs=1, max_stack_height=1),
                    Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000c02000300040005000204000000008000010001000102010002e30001005fe30002e450e4",
              EOFException.STACK_UNDERFLOW,
              id="callf_stack_validation_2"
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
