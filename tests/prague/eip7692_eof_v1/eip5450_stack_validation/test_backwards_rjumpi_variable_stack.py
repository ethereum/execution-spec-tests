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
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.PUSH1[0] + Op.RJUMPI[-5] + Op.STOP, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffb00",
              None,
              id="backwards_rjumpi_variable_stack_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] + Op.STOP, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000045f6000e100025f5f5f506000e1fff900",
              None,
              id="backwards_rjumpi_variable_stack_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] + Op.PUSH1[0] + Op.RJUMPI[-12] + Op.STOP, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000045f6000e100025f5f5f506000e1fff96000e1fff400",
              None,
              id="backwards_rjumpi_variable_stack_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] + Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[-13] + Op.STOP, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000055f6000e100025f5f5f506000e1fff95f6000e1fff300",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpi_variable_stack_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.PUSH1[1] + Op.ADD + Op.DUP1 + Op.RJUMPI[-7] + Op.STOP, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000055f6000e100025f5f5f60010180e1fff900",
              None,
              id="backwards_rjumpi_variable_stack_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.PUSH1[1] + Op.ADD + Op.DUP1 * 2 + Op.RJUMPI[-8] + Op.STOP, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000055f6000e100025f5f5f6001018080e1fff800",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpi_variable_stack_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 5 + Op.POP + Op.RJUMPI[-4] + Op.STOP, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000055f6000e100025f5f5f5f5f50e1fffc00",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpi_variable_stack_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] + Op.RJUMP[-10], max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000045f6000e100025f5f5f506000e1fff9e0fff6",
              None,
              id="backwards_rjumpi_variable_stack_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] + Op.PUSH0 + Op.RJUMP[-11], max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000045f6000e100025f5f5f506000e1fff95fe0fff5",
              EOFException.STACK_HEIGHT_MISMATCH,
              id="backwards_rjumpi_variable_stack_8"
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
