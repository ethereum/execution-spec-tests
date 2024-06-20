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
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xfffb] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000016000e1fffb00",
                None,
                id="backwards_rjumpi_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000804000000008000015f506000e1fff900",
                None,
                id="backwards_rjumpi_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.PUSH1[0x00] + Op.RJUMPI[0xfff4] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000d04000000008000015f506000e1fff96000e1fff400",
                None,
                id="backwards_rjumpi_different_locations_same_target",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0xfff3] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000025f506000e1fff95f6000e1fff300",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpi_different_locations_same_target_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 + Op.RJUMPI[0xfff9] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000025f60010180e1fff900",
                None,
                id="backwards_rjumpi_valid_loop",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x01] + Op.ADD + Op.DUP1 * 2 + Op.RJUMPI[0xfff8] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000a04000000008000025f6001018080e1fff800",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpi_pushing_loop",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 3 + Op.POP + Op.RJUMPI[0xfffc] + Op.STOP, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000804000000008000025f5f5f50e1fffc00",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpi_popping_loop",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.RJUMP[0xfff6], max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000a04000000008000015f506000e1fff9e0fff6",
                None,
                id="rjumpi_rjump_same_target_equal_stack",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff9] + Op.PUSH0 + Op.RJUMP[0xfff5], max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000015f506000e1fff95fe0fff5",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="rjump_rjumpi_same_target_different_stack",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0xfff5] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000d04000000008000035f6000e100015f6000e1fff500",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpi_max_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH1[0xbe] + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.POP + Op.PUSH1[0x00] + Op.RJUMPI[0xfff5] + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e040000000080000360be6000e10001506000e1fff500",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjumpi_min_stack_height_mismatch",
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
