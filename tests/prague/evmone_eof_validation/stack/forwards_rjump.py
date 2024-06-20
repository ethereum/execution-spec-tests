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
                        Section.Code(code=Op.RJUMP[0x0000] + Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100040400000000800000e0000000",
                None,
                id="forwards_rjump_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0003] + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000025f6000e10003e000011900",
                None,
                id="forwards_rjump_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0008] + Op.PUSH1[0x00] + Op.RJUMPI[0x0006] + Op.RJUMP[0x0004] + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001304000000008000025f6000e100086000e10006e00004e000011900",
                None,
                id="forwards_rjump_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0003] + Op.RJUMP[0x0001] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000025f6000e10003e000015f00",
                None,
                id="forwards_rjump_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0008] + Op.PUSH1[0x00] + Op.RJUMPI[0x0007] + Op.RJUMP[0x0005] + Op.PUSH0 + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000025f6000e100086000e10007e000055fe000011900",
                None,
                id="forwards_rjump_5",
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
