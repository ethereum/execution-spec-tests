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
                        0x02,
                        0x04,
                        0x00,
                        0x00,
                        0x00,

                     ]),
                ),
                "0xef0001010004020001000204000000",
                EOFException.INVALID_SECTION_BODIES_SIZE,
                id="EOF1_truncated_section_1",
            ),
            pytest.param(
            Container(
                name="EOF1V00002",
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
                        0x02,
                        0x04,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,

                     ]),
                ),
                "0xef0001010004020001000204000000008000",
                EOFException.INVALID_SECTION_BODIES_SIZE,
                id="EOF1_truncated_section_2",
            ),
            pytest.param(
            Container(
                name="EOF1V00003",
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
                        0x02,
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
                ),
                "0xef000101000402000100020400000000800000fe",
                EOFException.INVALID_SECTION_BODIES_SIZE,
                id="EOF1_truncated_section_3",
            ),
            
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.PUSH1[0x00] + Op.RETURNCONTRACT[0x00], max_stack_height=2),
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
                                      0x02,
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
                "0xef000101000402000100060300010014040000000080000260026000ee00ef000101000402000100010400020000800000fe",
                None,
                id="EOF1_truncated_section_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.PUSH1[0x00] + Op.RETURNCONTRACT[0x00], max_stack_height=2),
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
                                      0x02,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xfe,
                                      0xaa,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.INITCODE,
                ),
                "0xef000101000402000100060300010015040000000080000260016000ee00ef000101000402000100010400020000800000feaa",
                None,
                id="EOF1_truncated_section_5",
            ),
                pytest.param(
            Container(
                name="EOF1V00006",
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
                        0x02,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xfe,

                     ]),
                ),
                "0xef000101000402000100010400020000800000fe",
                EOFException.TOPLEVEL_CONTAINER_TRUNCATED,
                id="EOF1_truncated_section_6",
            ),
            pytest.param(
            Container(
                name="EOF1V00007",
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
                        0x02,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xfe,
                        0xaa,

                     ]),
                ),
                "0xef000101000402000100010400020000800000feaa",
                EOFException.TOPLEVEL_CONTAINER_TRUNCATED,
                id="EOF1_truncated_section_7",
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
