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
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.RJUMP[-5], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000015f50e0fffb",
              None,
              id="backwards_rjump_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[1] + Op.RJUMPI[3] + Op.RJUMP[-8] + Op.RJUMP[-11], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000015f506001e10003e0fff8e0fff5",
              None,
              id="backwards_rjump_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[1] + Op.RJUMPI[3] + Op.RJUMP[-8] + Op.PUSH0 + Op.RJUMP[-12], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000015f506001e10003e0fff85fe0fff4",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjump_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.RJUMP[-4], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000015fe0fffc",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjump_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.RJUMP[-4], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000015f50e0fffc",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjump_5"
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
