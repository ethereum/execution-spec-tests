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
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[-6] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000704000000008000016000e200fffa00",
                None,
                id="backwards_rjumpv_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000015f506000e200fff800",
                None,
                id="backwards_rjumpv_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH1[0x00] + Op.RJUMPV[-14] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f04000000008000015f506000e200fff86000e200fff200",
                None,
                id="backwards_rjumpv_different_locations_same_target",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPV[-15] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000025f506000e200fff85f6000e200fff100",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_different_locations_same_target_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.RJUMP[0xfff5], max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000015f506000e200fff8e0fff5",
                None,
                id="rjumpv_rjump_same_target_equal_stack",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-8] + Op.PUSH0 + Op.RJUMP[0xfff4], max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000015f506000e200fff85fe0fff4",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="rjump_rjumpv_same_target_different_stack",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000035f6000e100015f6000e200fff400",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_max_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH1[0xbe] + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.POP + Op.PUSH1[0x00] + Op.RJUMPV[-12] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f040000000080000360be6000e10001506000e200fff400",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpv_min_stack_height_mismatch",
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
