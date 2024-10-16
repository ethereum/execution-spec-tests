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
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.TLOAD, code_outputs=1, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010003040000000001000060005c",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.INVALID, code_inputs=1, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000001800000fe",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.TLOAD, code_inputs=2, code_outputs=3, max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010003040000000203000060005c",
              EOFException.INVALID_FIRST_SECTION_TYPE,
              id="eof1_invalid_section_0_type_3"
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
