""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "12ca2f0bd2f7380100e154aaaa0995c46cbb2710"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.CALLCODE, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000f2",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.SELFDESTRUCT, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000ff",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.JUMP, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000056",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.JUMPI, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000057",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PC, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000058",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.CALL, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000f1",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.STATICCALL, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000fa",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.DELEGATECALL, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000f4",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.CREATE, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000f0",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.CREATE2, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000f5",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.CODESIZE, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000038",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.CODECOPY, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000039",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=Op.EXTCODESIZE, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000003b",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_12"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0014',
                sections = [
                    Section.Code(code=Op.EXTCODECOPY, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000003c",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_13"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0015',
                sections = [
                    Section.Code(code=Op.EXTCODEHASH, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000003f",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_14"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0016',
                sections = [
                    Section.Code(code=Op.GAS, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000005a",
              EOFException.UNDEFINED_INSTRUCTION,
              id="deprecated_instructions_15"
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
