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
                    Section.Code(code=Op.PUSH0 + Op.RJUMPI[7] + Op.PUSH0 * 3 + Op.RJUMPI[1] + Op.POP + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000045fe100075f5f5fe10001505f5ffd",
              None,
              id="non_constant_stack_height_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 * 2 + Op.RJUMPI[7] + Op.PUSH0 * 3 + Op.RJUMPI[1] + Op.POP + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000055f5fe100075f5f5fe10001505f5ffd",
              None,
              id="non_constant_stack_height_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.RJUMPI[7] + Op.PUSH0 * 3 + Op.RJUMPI[1] + Op.POP * 2 + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000045fe100075f5f5fe1000150505f5ffd",
              EOFException.STACK_UNDERFLOW,
              id="non_constant_stack_height_2"
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
