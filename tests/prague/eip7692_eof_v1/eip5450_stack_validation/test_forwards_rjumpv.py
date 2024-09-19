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
                    Section.Code(code=Op.PUSH1[1] + Op.RJUMPV[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000016001e200000000",
              None,
              id="forwards_rjumpv_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000025f6000e20000011900",
              None,
              id="forwards_rjumpv_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[2,3] + Op.PUSH0 + Op.POP + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000025f6000e201000200035f501900",
              None,
              id="forwards_rjumpv_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[1] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000025f6000e20000015f00",
              None,
              id="forwards_rjumpv_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[1,2] + Op.PUSH0 * 2 + Op.NOT + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000035f6000e201000100025f5f1900",
              None,
              id="forwards_rjumpv_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[5,10] + Op.PUSH1[1] + Op.RJUMP[7] + Op.PUSH1[2] + Op.RJUMP[2] + Op.PUSH1[3] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000025f6000e2010005000a6001e000076002e00002600300",
              None,
              id="forwards_rjumpv_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[4,9] + Op.PUSH0 + Op.RJUMP[8] + Op.PUSH0 * 2 + Op.RJUMP[3] + Op.PUSH0 * 3 + Op.STOP, max_stack_height=4),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000045f6000e201000400095fe000085f5fe000035f5f5f00",
              None,
              id="forwards_rjumpv_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH0 * 4 + Op.PUSH1[0] + Op.RJUMPV[4,9] + Op.POP + Op.RJUMP[8] + Op.POP * 2 + Op.RJUMP[3] + Op.POP * 3 + Op.STOP, max_stack_height=5),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000055f5f5f5f6000e2010004000950e000085050e0000350505000",
              None,
              id="forwards_rjumpv_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[3] + Op.RJUMP[0] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000025f6000e2000003e0000000",
              None,
              id="forwards_rjumpv_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPV[4] + Op.PUSH0 + Op.RJUMP[0] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000025f6000e20000045fe0000000",
              None,
              id="forwards_rjumpv_9"
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
