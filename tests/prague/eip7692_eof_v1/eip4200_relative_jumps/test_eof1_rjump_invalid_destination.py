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
                    Section.Code(code=Op.RJUMP[-5] + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100040400000000800000e0fffb00",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.RJUMP[-13] + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100040400000000800000e0fff300",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.RJUMP[2] + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100040400000000800000e0000200",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.RJUMP[-4] + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006000e0fffc00",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.RJUMP[9] + Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[0] + Op.POP + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0007_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000f03000100140400000000800004e00009600060ff60006000ec005000ef000101000402000100010400000000800000fe",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.RJUMP[5] + Op.PUSH1[0] * 2 + Op.RETURNCONTRACT[0], max_stack_height=2),
                    Section.Container(container=Container(
                        name = 'EOFV1_0008_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
                kind=ContainerKind.INITCODE
              )
              ,
              "ef0001010004020001000903000100140400000000800002e0000560006000ee00ef000101000402000100010400000000800000fe",
              EOFException.INVALID_RJUMP_DESTINATION,
              id="eof1_rjump_invalid_destination_7"
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
