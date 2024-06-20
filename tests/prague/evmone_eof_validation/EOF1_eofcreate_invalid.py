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
                        Section.Code(code=Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V1_CS1",
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
                "0xef0001010004020001000903000100140400000000800004600060ff60006000ecef000101000402000100010400000000800000fe",
                EOFException.TRUNCATED_INSTRUCTION,
                id="eofcreate_with_truncated_immediate",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0x00], max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V2_CS1",
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
                "0xef0001010004020001000a03000100140400000000800004600060ff60006000ec00ef000101000402000100010400000000800000fe",
                EOFException.MISSING_STOP_OPCODE,
                id="eofcreate_as_last_instruction",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0x01] + Op.POP + Op.STOP, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V3_CS1",
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
                "0xef0001010004020001000c03000100140400000000800004600060ff60006000ec015000ef000101000402000100010400000000800000fe",
                EOFException.INVALID_CONTAINER_SECTION_INDEX,
                id="eofcreate_to_non_existent_container_section_a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0xff] + Op.POP + Op.STOP, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V4_CS1",
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
                "0xef0001010004020001000c03000100140400000000800004600060ff60006000ecff5000ef000101000402000100010400000000800000fe",
                EOFException.INVALID_CONTAINER_SECTION_INDEX,
                id="eofcreate_to_non_existent_container_section_b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.PUSH1[0xff] + Op.PUSH1[0x00] * 2 + Op.EOFCREATE[0x00] + Op.POP + Op.STOP, max_stack_height=4),
                        Section.Container(
                            container=Container(
                              name="EOF1V5_CS1",
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
                                      0x03,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xfe,
                                      0xaa,
                                      0xbb,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c03000100160400000000800004600060ff60006000ec005000ef000101000402000100010400030000800000feaabb",
                EOFException.EOF_CREATE_WITH_TRUNCATED_CONTAINER,
                id="eofcreate_to_container_with_truncated_data",
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
