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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.RJUMP[0xfffd], max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000b04000000008000035f6000e100025f5fe0fffd",
                None,
                id="backwards_rjump_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.RJUMP[0xfffb], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000d04000000008000045f6000e100025f5f5f50e0fffb",
                None,
                id="backwards_rjump_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x01] + Op.RJUMPI[0x0003] + Op.RJUMP[0xfff8] + Op.RJUMP[0xfff5], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001504000000008000045f6000e100025f5f5f506001e10003e0fff8e0fff5",
                None,
                id="backwards_rjump_different_locations_same_target",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.PUSH1[0x01] + Op.RJUMPI[0x0003] + Op.RJUMP[0xfff8] + Op.PUSH0 + Op.RJUMP[0xfff4], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001604000000008000045f6000e100025f5f5f506001e10003e0fff85fe0fff4",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjump_different_locations_same_target_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.PUSH0 + Op.RJUMP[0xfff9], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000045f6000e100025f5f6000e100015fe0fff9",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjump_max_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.PUSH1[0x00] + Op.RJUMPI[0x0001] + Op.POP + Op.RJUMP[0xfff9], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001104000000008000045f6000e100025f5f6000e1000150e0fff9",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="backwards_rjump_min_stack_height_mismatch",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.RJUMP[0xfffc], max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000c04000000008000045f6000e100025f5f5fe0fffc",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="infinite_pushing_loop",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 3 + Op.POP + Op.RJUMP[0xfffc], max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000d04000000008000035f6000e100025f5f5f50e0fffc",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="infinite_popping_loop",
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
