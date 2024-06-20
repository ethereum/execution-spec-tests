"""
EOF v1 validation code
"""

import pytest
from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools import EOFException, Opcodes as Op, UndefinedOpcodes as UOp
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        
        pytest.param(
                Container(
                    name="EOF1V00001",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[-23] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e200ffe9600100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e200fff8600100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[-1] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e200ffff600100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[3] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e2000003600100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[4] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e2000004600100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,-27] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e20200000003ffe5600100600200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,-12] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e20200000003fff4600100600200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,-1] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e20200000003ffff600100600200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,6] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e202000000030006600100600200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,7] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e202000000030007600100600200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="EOF1_rjumpv_invalid_destination_10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[9] + Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0x00] + Op.POP + Op.STOP, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V11_CS1",
                              raw_bytes=bytes(
                                   [
  
                                      0xef,
                                      0x00,
                                      0x01,
                                      0x01,
                                      0x00,
                                      0x04,
                                      0x02,
                                      0x00,
                                      0x01,
                                      0x00,
                                      0x01,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xfe,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010012030001001404000000008000046000e2000009600060ff60006000ec005000ef000101000402000100010400000000800000fe",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpv_target_eofcreate_immediate",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[5] + Op.PUSH1[0x00] * 2 + Op.RETURNCONTRACT[0x00], max_stack_height=2),
                        Section.Container(
                            container=Container(
                              name="EOF1V12_CS1",
                              raw_bytes=bytes(
                                   [
  
                                      0xef,
                                      0x00,
                                      0x01,
                                      0x01,
                                      0x00,
                                      0x04,
                                      0x02,
                                      0x00,
                                      0x01,
                                      0x00,
                                      0x01,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xfe,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.INITCODE,
                ),
                "0xef0001010004020001000c030001001404000000008000026000e200000560006000ee00ef000101000402000100010400000000800000fe",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpv_target_returncontract_immediate",
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
    if expected_hex_bytecode[0:2] == "0x":
        expected_hex_bytecode = expected_hex_bytecode[2:]
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
