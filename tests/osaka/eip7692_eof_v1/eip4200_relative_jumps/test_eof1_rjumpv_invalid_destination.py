""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section, ContainerKind

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4200.md"
REFERENCE_SPEC_VERSION = "b452cf8a47e5b5bf08a1576a4dfaf828306beb5a"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[-23] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e200ffe9600100",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[-8] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e200fff8600100",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[-1] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e200ffff600100",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[3] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e2000003600100",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[4] + Op.PUSH1[1] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000016000e2000004600100",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,-27] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e20200000003ffe5600100600200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,-12] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e20200000003fff4600100600200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,-1] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e20200000003ffff600100600200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,6] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e202000000030006600100600200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.PUSH1[2] + Op.RJUMPV[0,3,7] + Op.PUSH1[1] + Op.STOP + Op.PUSH1[2] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016002e202000000030007600100600200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[9] + Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[0] + Op.POP + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0011_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef00010100040200010012030001001404000000008000046000e2000009600060ff60006000ec005000ef000101000402000100010400000000800000fe",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMPV[5] + Op.PUSH1[0] * 2 + Op.RETURNCONTRACT[0], max_stack_height=2),
                    Section.Container(container=Container(
                        name = 'EOFV1_0012_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
                kind=ContainerKind.INITCODE
              )
              ,
              "ef0001010004020001000c030001001404000000008000026000e200000560006000ee00ef000101000402000100010400000000800000fe",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjumpv_invalid_destination_11"
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
