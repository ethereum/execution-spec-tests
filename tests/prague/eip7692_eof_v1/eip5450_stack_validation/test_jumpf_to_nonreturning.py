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
                    Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=2),
                    Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010008020002000500010400000000800002008000005f5fe5000100",
              None,
              id="jumpf_to_nonreturning_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[1], max_stack_height=3),
                    Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010008020002000600010400000000800003038000035f5f5fe5000100",
              None,
              id="jumpf_to_nonreturning_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[1], max_stack_height=4),
                    Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010008020002000700010400000000800004038000035f5f5f5fe5000100",
              None,
              id="jumpf_to_nonreturning_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=2),
                    Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010008020002000500010400000000800002038000035f5fe5000100",
              EOFException.STACK_UNDERFLOW,
              id="jumpf_to_nonreturning_3"
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
