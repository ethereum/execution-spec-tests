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
                        Section.Code(code=Op.PUSH1[0x00] * 4 + Op.EOFCREATE[0x00] + Op.STOP, max_stack_height=4),
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
                                      0x08,
                                      0x02,
                                      0x00,
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
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xfe,
                                      0xfe,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b030001001b04000000008000046000600060006000ec0000ef000101000802000200010001040000000080000000800000fefe",
                EOFException.UNREACHABLE_CODE_SECTIONS,
                id="EOF1_subcontainer_containing_unreachable_code_sections_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] * 4 + Op.EOFCREATE[0x00] + Op.STOP, max_stack_height=4),
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
                                      0x14,
                                      0x02,
                                      0x00,
                                      0x05,
                                      0x00,
                                      0x03,
                                      0x00,
                                      0x03,
                                      0x00,
                                      0x01,
                                      0x00,
                                      0x03,
                                      0x00,
                                      0x03,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x00,
                                      0xe5,
                                      0x00,
                                      0x01,
                                      0xe5,
                                      0x00,
                                      0x02,
                                      0xfe,
                                      0xe5,
                                      0x00,
                                      0x04,
                                      0xe5,
                                      0x00,
                                      0x03,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b030001003804000000008000046000600060006000ec0000ef000101001402000500030003000100030003040000000080000000800000008000000080000000800000e50001e50002fee50004e50003",
                EOFException.UNREACHABLE_CODE_SECTIONS,
                id="EOF1_subcontainer_containing_unreachable_code_sections_2",
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
