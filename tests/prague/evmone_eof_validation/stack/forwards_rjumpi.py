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
                        Section.Code(code=Op.PUSH1[0x01] + Op.RJUMPI[0x0000] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016001e1000000",
                None,
                id="forwards_rjumpi_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000804000000008000025f6000e100011900",
                None,
                id="forwards_rjumpi_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0006] + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000d04000000008000025f6000e100066000e100011900",
                None,
                id="forwards_rjumpi_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000804000000008000025f6000e100015f00",
                None,
                id="forwards_rjumpi_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0007] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000035f6000e100075f6000e100011900",
                None,
                id="forwards_rjumpi_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 + Op.PUSH1[0x0a] + Op.GT + Op.RJUMPI[0x0004] + Op.DUP1 + Op.RJUMPI[0xfff2] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000035f60010180600a11e1000480e1fff200",
                None,
                id="forwards_rjumpi_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 + Op.PUSH1[0x0a] + Op.GT + Op.RJUMPI[0x0005] + Op.PUSH0 + Op.DUP1 + Op.RJUMPI[0xfff3] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000035f60010180600a11e100055f80e1fff300",
                None,
                id="forwards_rjumpi_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0001] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000025f6000e100045fe000015f00",
                None,
                id="forwards_rjumpi_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000025f6000e100045fe000011900",
                None,
                id="forwards_rjumpi_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.POP + Op.RJUMP[0x0001] + Op.POP + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000025f6000e1000450e000015000",
                None,
                id="forwards_rjumpi_10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.POP + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000025f6000e1000450e000011900",
                None,
                id="forwards_rjumpi_11",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0003] + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000a04000000008000025f6000e10003e0000000",
                None,
                id="forwards_rjumpi_12",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000025f6000e100045fe0000000",
                None,
                id="forwards_rjumpi_13",
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
