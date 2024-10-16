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
                  name="EOFV1_0001",
                  raw_bytes=(
                    [
                      0xef, 0x00, 0x01, # Version: 1
                      0x01, 0x00, 0x08, # Types Length: 8
                      0x02, 0x00, 0x02, # Code Sections (Length: 2)
                            0x00, 0x01, #   Code Section 0 (Length: 1)
                            0x00, 0x01, #   Code Section 1 (Length: 1)
                      #--- Error: Invalid Data Header ---#
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0x00,
                      0x80,
                      0x00,
                      0x00,
                      0xfe,
                      0xfe,
                    ]),
              )
              ,
              "ef000101000802000200010001000080000000800000fefe",
              EOFException.MISSING_DATA_SECTION,
              id="no_data_section"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.POP + Op.CALLF[2] + Op.POP + Op.RETF, code_inputs=1, code_outputs=0, max_stack_height=1),
                    Section.Code(code=Op.ADDRESS + Op.DUP1 + Op.CALLF[3] + Op.POP * 2 + Op.RETF, code_outputs=1, max_stack_height=3),
                    Section.Code(code=Op.DUP1 + Op.RETF, code_inputs=2, code_outputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010010020004000500060008000204000000008000010100000100010003020300035fe300010050e3000250e43080e300035050e480e4",
              None,
              id="non_void_input_output"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.INVALID, max_stack_height=0),
                    Section.Data(data="da")
                ],
              )
              ,
              "ef000101000802000200030001040001000080000000800000e50001feda",
              None,
              id="with_data_section"
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
