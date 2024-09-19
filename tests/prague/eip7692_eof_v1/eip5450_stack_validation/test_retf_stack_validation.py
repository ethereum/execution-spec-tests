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
                    Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef000101000802000200040003040000000080000200020002e30001005f5fe4",
              None,
              id="retf_stack_validation_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=2, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000802000200040002040000000080000200020001e30001005fe4",
              EOFException.STACK_UNDERFLOW,
              id="retf_stack_validation_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 3 + Op.RETF, code_outputs=2, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
              EOFException.STACK_HIGHER_THAN_OUTPUTS,
              id="retf_stack_validation_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.STOP, max_stack_height=2),
                    Section.Code(code=Op.RJUMPI[7] + Op.PUSH1[1] * 2 + Op.RJUMP[2] + Op.PUSH0 * 2 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
              )
              ,
              "ef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
              None,
              id="retf_stack_validation_3"
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
