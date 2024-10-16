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
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[-6] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000016000e200fffa00",
              None,
              id="backwards_rjumpv_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-8] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000015f506000e200fff800",
              None,
              id="backwards_rjumpv_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-8] + Op.PUSH1[0] + Op.RJUMPV[-14] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000015f506000e200fff86000e200fff200",
              None,
              id="backwards_rjumpv_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-8] + Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[-15] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000025f506000e200fff85f6000e200fff100",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpv_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-8] + Op.RJUMP[-11], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000015f506000e200fff8e0fff5",
              None,
              id="backwards_rjumpv_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-8] + Op.PUSH0 + Op.RJUMP[-12], max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000015f506000e200fff85fe0fff4",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpv_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000035f6000e100015f6000e200fff400",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpv_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH1[190] + Op.PUSH1[0] + Op.RJUMPI[1] + Op.POP + Op.PUSH1[0] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000f040000000080000360be6000e10001506000e200fff400",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpv_7"
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
