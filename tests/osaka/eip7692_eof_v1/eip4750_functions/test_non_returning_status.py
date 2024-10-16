""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "76c94b69eccb06786fe0b95213ff209fa9aef7c1"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000802000200030001040000000080000000800000e5000100",
              None,
              id="non_returning_status_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=0),
                    Section.Code(code=Op.JUMPF[2], code_outputs=0, max_stack_height=0),
                    Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000c02000300040003000104000000008000000000000000000000e3000100e50002e4",
              None,
              id="non_returning_status_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[2], code_inputs=1, code_outputs=0, max_stack_height=1),
                    Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000c020003000500070001040000000080000101000001000000005fe3000100e10001e4e50002e4",
              None,
              id="non_returning_status_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.STOP, max_stack_height=1),
                    Section.Code(code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[0], code_inputs=1, code_outputs=0, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010008020002000500070400000000800001010000015fe3000100e10001e4e50000",
              None,
              id="non_returning_status_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.JUMPF[0], code_outputs=0, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000802000200030003040000000080000000000000e50001e50000",
              EOFException.INVALID_NON_RETURNING_FLAG,
              id="non_returning_status_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.JUMPF[1], max_stack_height=1),
                    Section.Code(code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[2], code_inputs=1, max_stack_height=1),
                    Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000c020003000400070001040000000080000101800001000000005fe50001e10001e4e50002e4",
              EOFException.INVALID_NON_RETURNING_FLAG,
              id="non_returning_status_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.JUMPF[1], max_stack_height=1),
                    Section.Code(code=Op.RJUMPI[1] + Op.RETF + Op.JUMPF[0], code_inputs=1, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010008020002000400070400000000800001018000015fe50001e10001e4e50000",
              EOFException.INVALID_NON_RETURNING_FLAG,
              id="non_returning_status_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    Section.Code(code=Op.JUMPF[2], max_stack_height=0),
                    Section.Code(code=Op.JUMPF[1], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000c02000300030003000304000000008000000080000000800000e50001e50002e50001",
              None,
              id="non_returning_status_12"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0014',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=0),
                    Section.Code(code=Op.JUMPF[2], code_outputs=0, max_stack_height=0),
                    Section.Code(code=Op.JUMPF[1], code_outputs=0, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000c02000300040003000304000000008000000000000000000000e3000100e50002e50001",
              None,
              id="non_returning_status_13"
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
