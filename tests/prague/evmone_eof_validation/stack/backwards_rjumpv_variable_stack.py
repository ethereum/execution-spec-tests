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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.PUSH1[0x00] + Op.RJUMPV[-6] + Op.STOP, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f04000000008000045f6000e100025f5f6000e200fffa00",
                None,
                id="backwards_rjumpv_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.STOP, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000045f6000e100025f5f5f506000e200fff800",
                None,
                id="backwards_rjumpv_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH1[0x00] + Op.RJUMPV[-14] + Op.STOP, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001704000000008000045f6000e100025f5f5f506000e200fff86000e200fff200",
                None,
                id="backwards_rjumpv_variable_stack_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPV[-15] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001804000000008000055f6000e100025f5f5f506000e200fff85f6000e200fff100",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_variable_stack_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.RJUMP[0xfff5], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001304000000008000045f6000e100025f5f5f506000e200fff8e0fff5",
                None,
                id="backwards_rjumpv_variable_stack_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH0 + Op.RJUMP[0xfff4], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000045f6000e100025f5f5f506000e200fff85fe0fff4",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_variable_stack_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001604000000008000055f6000e100025f5f5f6000e100015f6000e200fff400",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_variable_stack_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 4 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001704000000008000055f6000e100025f5f5f5f6000e10001506000e200fff400",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_variable_stack_8",
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
