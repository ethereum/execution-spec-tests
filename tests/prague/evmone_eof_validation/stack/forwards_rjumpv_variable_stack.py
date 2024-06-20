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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.PUSH1[0x01] + Op.RJUMPV[0] + Op.STOP, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f04000000008000045f6000e100025f5f6001e200000000",
                None,
                id="forwards_rjumpv_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[1] + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000011900",
                None,
                id="forwards_rjumpv_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[2,3] + Op.PUSH0 + Op.POP + Op.NOT + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001504000000008000055f6000e100025f5f5f6000e201000200035f501900",
                None,
                id="forwards_rjumpv_variable_stack_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[1] + Op.PUSH0 + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000015f00",
                None,
                id="forwards_rjumpv_variable_stack_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[1,2] + Op.PUSH0 * 2 + Op.NOT + Op.STOP, max_stack_height=6),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001504000000008000065f6000e100025f5f5f6000e201000100025f5f1900",
                None,
                id="forwards_rjumpv_variable_stack_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[5,10] + Op.PUSH1[0x01] + Op.RJUMP[0x0007] + Op.PUSH1[0x02] + Op.RJUMP[0x0002] + Op.PUSH1[0x03] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001e04000000008000055f6000e100025f5f5f6000e2010005000a6001e000076002e00002600300",
                None,
                id="forwards_rjumpv_variable_stack_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[4,9] + Op.PUSH0 + Op.RJUMP[0x0008] + Op.PUSH0 * 2 + Op.RJUMP[0x0003] + Op.PUSH0 * 3 + Op.STOP, max_stack_height=7),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001e04000000008000075f6000e100025f5f5f6000e201000400095fe000085f5fe000035f5f5f00",
                None,
                id="forwards_rjumpv_variable_stack_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 6 + Op.PUSH1[0x00] + Op.RJUMPV[4,9] + Op.POP + Op.RJUMP[0x0008] + Op.POP * 2 + Op.RJUMP[0x0003] + Op.POP * 3 + Op.STOP, max_stack_height=8),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001002104000000008000085f6000e100025f5f5f5f5f5f6000e2010004000950e000085050e0000350505000",
                None,
                id="forwards_rjumpv_variable_stack_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[3] + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001304000000008000055f6000e100025f5f5f6000e2000003e0000000",
                None,
                id="forwards_rjumpv_variable_stack_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPV[4] + Op.PUSH0 + Op.RJUMP[0x0000] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000055f6000e100025f5f5f6000e20000045fe0000000",
                None,
                id="forwards_rjumpv_variable_stack_10",
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
