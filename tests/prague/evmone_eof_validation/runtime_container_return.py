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
                        Section.Code(code=Op.PUSH1[0x00] * 2 + Op.RETURN, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010005040000000080000260006000f3",
                None,
                id="runtime_container_return_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] * 2 + Op.RETURNCONTRACT[0x00], max_stack_height=2),
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
                                      0x05,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x02,
                                      0x60,
                                      0x00,
                                      0x60,
                                      0x00,
                                      0xf3,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.INITCODE,
                ),
                "0xef000101000402000100060300010018040000000080000260006000ee00ef00010100040200010005040000000080000260006000f3",
                None,
                id="runtime_container_return_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] * 4 + Op.EOFCREATE[0x00] + Op.STOP, max_stack_height=4),
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
                                      0x06,
                                      0x03,
                                      0x00,
                                      0x01,
                                      0x00,
                                      0x18,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x02,
                                      0x60,
                                      0x00,
                                      0x60,
                                      0x00,
                                      0xee,
                                      0x00,
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
                                      0x05,
                                      0x04,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x00,
                                      0x80,
                                      0x00,
                                      0x02,
                                      0x60,
                                      0x00,
                                      0x60,
                                      0x00,
                                      0xf3,

                                   ]),
                            )
                        ),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b030001003604000000008000046000600060006000ec0000ef000101000402000100060300010018040000000080000260006000ee00ef00010100040200010005040000000080000260006000f3",
                None,
                id="runtime_container_return_3",
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
