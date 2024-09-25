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
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[0] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e70000",
              None,
              id="swapn_stack_validation_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[18] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e71200",
              None,
              id="swapn_stack_validation_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[19] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e71300",
              EOFException.STACK_UNDERFLOW,
              id="swapn_stack_validation_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[208] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7d000",
              EOFException.STACK_UNDERFLOW,
              id="swapn_stack_validation_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[254] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7fe00",
              EOFException.STACK_UNDERFLOW,
              id="swapn_stack_validation_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH1[1] * 20 + Op.SWAPN[255] + Op.STOP, max_stack_height=20),
                    ],
              )
              ,
              "ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7ff00",
              EOFException.STACK_UNDERFLOW,
              id="swapn_stack_validation_5"
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
