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
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=5),
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF, code_outputs=5, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200040009040000000080000500050003e30001005f6000e100025f5fe4",
              EOFException.STACK_UNDERFLOW,
              id="retf_variable_stack_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF, code_outputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200040009040000000080000300030003e30001005f6000e100025f5fe4",
              EOFException.STACK_UNDERFLOW,
              id="retf_variable_stack_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF, code_outputs=1, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200040009040000000080000100010003e30001005f6000e100025f5fe4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="retf_variable_stack_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=0),
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF, code_outputs=0, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200040009040000000080000000000003e30001005f6000e100025f5fe4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="retf_variable_stack_3"
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
