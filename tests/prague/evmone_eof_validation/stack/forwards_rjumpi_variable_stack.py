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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.PUSH1[0x01] + Op.RJUMPI[0x0000] + Op.STOP, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000045f6000e100025f5f6001e1000000",
                None,
                id="forwards_rjumpi_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000055f6000e100025f5f5f6000e100011900",
                None,
                id="forwards_rjumpi_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0006] + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001504000000008000055f6000e100025f5f5f6000e100066000e100011900",
                None,
                id="forwards_rjumpi_variable_stack_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000055f6000e100025f5f5f6000e100015f00",
                None,
                id="forwards_rjumpi_variable_stack_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0007] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.NOT + Op.STOP, max_stack_height=6),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001604000000008000065f6000e100025f5f5f6000e100075f6000e100011900",
                None,
                id="forwards_rjumpi_variable_stack_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 + Op.PUSH1[0x0a] + Op.GT + Op.RJUMPI[0x0004] + Op.DUP1 + Op.RJUMPI[0xfff2] + Op.STOP, max_stack_height=6),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001804000000008000065f6000e100025f5f5f60010180600a11e1000480e1fff200",
                None,
                id="forwards_rjumpi_variable_stack_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 + Op.PUSH1[0x0a] + Op.GT + Op.RJUMPI[0x0005] + Op.PUSH0 + Op.DUP1 + Op.RJUMPI[0xfff3] + Op.STOP, max_stack_height=6),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001904000000008000065f6000e100025f5f5f60010180600a11e100055f80e1fff300",
                None,
                id="forwards_rjumpi_variable_stack_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0001] + Op.PUSH0 + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000055f6000e100025f5f5f6000e100045fe000015f00",
                None,
                id="forwards_rjumpi_variable_stack_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000055f6000e100025f5f5f6000e100045fe000011900",
                None,
                id="forwards_rjumpi_variable_stack_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.POP + Op.RJUMP[0x0001] + Op.POP + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000055f6000e100025f5f5f6000e1000450e000015000",
                None,
                id="forwards_rjumpi_variable_stack_10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.POP + Op.RJUMP[0x0001] + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000055f6000e100025f5f5f6000e1000450e000011900",
                None,
                id="forwards_rjumpi_variable_stack_11",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0003] + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001204000000008000055f6000e100025f5f5f6000e10003e0000000",
                None,
                id="forwards_rjumpi_variable_stack_12",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0004] + Op.PUSH0 + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001304000000008000055f6000e100025f5f5f6000e100045fe0000000",
                None,
                id="forwards_rjumpi_variable_stack_13",
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
