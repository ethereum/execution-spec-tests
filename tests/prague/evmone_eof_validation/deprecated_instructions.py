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
                        Section.Code(code=Op.CALLCODE, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000f2",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CALLCODE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.SELFDESTRUCT, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000ff",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_SELFDESTRUCT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.JUMP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000056",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_JUMP",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.JUMPI, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000057",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_JUMPI",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PC, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000058",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_PC",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.CALL, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000f1",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.STATICCALL, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000fa",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_STATICCALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.DELEGATECALL, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000f4",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_DELEGATECALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.CREATE, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000f0",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CREATE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.CREATE2, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000f5",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CREATE2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.CODESIZE, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000038",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CODESIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.CODECOPY, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000039",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_CODECOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.EXTCODESIZE, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000104000000008000003b",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_EXTCODESIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00014",
                    sections=[
                        Section.Code(code=Op.EXTCODECOPY, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000104000000008000003c",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_EXTCODECOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00015",
                    sections=[
                        Section.Code(code=Op.EXTCODEHASH, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000104000000008000003f",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_EXTCODEHASH",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00016",
                    sections=[
                        Section.Code(code=Op.GAS, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000104000000008000005a",
                EOFException.UNDEFINED_INSTRUCTION,
                id="deprecated_instruction_GAS",
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
