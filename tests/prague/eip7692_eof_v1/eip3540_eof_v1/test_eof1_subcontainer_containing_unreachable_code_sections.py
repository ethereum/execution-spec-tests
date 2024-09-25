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
                    Section.Code(code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0001_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000b030001001b04000000008000046000600060006000ec0000ef000101000802000200010001040000000080000000800000fefe",
              EOFException.UNREACHABLE_CODE_SECTIONS,
              id="eof1_subcontainer_containing_unreachable_code_sections_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0002_D1I0',
                        sections = [
                            Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                            Section.Code(code=Op.JUMPF[2], max_stack_height=0),
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            Section.Code(code=Op.JUMPF[4], max_stack_height=0),
                            Section.Code(code=Op.JUMPF[3], max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000b030001003804000000008000046000600060006000ec0000ef000101001402000500030003000100030003040000000080000000800000008000000080000000800000e50001e50002fee50004e50003",
              EOFException.UNREACHABLE_CODE_SECTIONS,
              id="eof1_subcontainer_containing_unreachable_code_sections_1"
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
