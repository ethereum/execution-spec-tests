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
                    Section.Code(code=Op.PUSH0, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000005f",
              EOFException.MISSING_STOP_OPCODE,
              id="no_terminating_instruction_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.PUSH1[1] + Op.ADD, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006002600101",
              EOFException.MISSING_STOP_OPCODE,
              id="no_terminating_instruction_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.RJUMPI[-5], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006001e1fffb",
              EOFException.MISSING_STOP_OPCODE,
              id="no_terminating_instruction_2"
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
