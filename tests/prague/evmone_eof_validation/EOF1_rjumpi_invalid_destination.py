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
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1fff900",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_before_code_section",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xffe7] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1ffe700",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_before_code_begin",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1000200",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_after_code_end",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1000100",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_code_end",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xffff] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1ffff00",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_same_rjumpi_immediate",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xfffc] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1fffc00",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_push_immediate",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0x0009] + Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0x00] + Op.POP + Op.STOP, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V7_CS1",
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
                "0xef00010100040200010011030001001404000000008000046000e10009600060ff60006000ec005000ef000101000402000100010400000000800000fe",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_eofcreate_immediate",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0x0005] + Op.PUSH1[0x00] * 2 + Op.RETURNCONTRACT[0x00], max_stack_height=2),
                        Section.Container(
                            container=Container(
                              name="EOF1V8_CS1",
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
                "0xef0001010004020001000b030001001404000000008000026000e1000560006000ee00ef000101000402000100010400000000800000fe",
                EOFException.INVALID_RJUMP_DESTINATION,
                id="rjumpi_target_returncontract_immediate",
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
