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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.LOG2 + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000a04000000008000035f6000e100025f5fa200",
                EOFException.STACK_UNDERFLOW,
                id="log2_underflow",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.ADD + Op.STOP, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000a04000000008000035f6000e100025f5f0100",
                EOFException.STACK_UNDERFLOW,
                id="add_underflow",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=4),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=4, code_outputs=5, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000c00020400000000800004040500055f6000e100025f5fe30001005fe4",
                EOFException.STACK_UNDERFLOW,
                id="callf_underflow_a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=4),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=3, code_outputs=4, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000c00020400000000800004030400045f6000e100025f5fe30001005fe4",
                EOFException.STACK_UNDERFLOW,
                id="callf_underflow_b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=5, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000304000000008000030003000305030003e30001005f6000e100025f5fe500025050e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_underflow_a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.RETF, code_inputs=3, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000104000000008000030003000303030003e30001005f6000e100025f5fe50002e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_underflow_b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.PUSH1[0x00] * 2 + Op.REVERT, code_inputs=5, max_stack_height=7),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00050400000000800003058000075f6000e100025f5fe5000160006000fd",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_underflow_c",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.PUSH1[0x00] * 2 + Op.REVERT, code_inputs=3, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00050400000000800003038000055f6000e100025f5fe5000160006000fd",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_underflow_d",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=5),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.RETF, code_outputs=5, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040009040000000080000500050003e30001005f6000e100025f5fe4",
                EOFException.STACK_UNDERFLOW,
                id="retf_underflow_a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.RETF, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040009040000000080000300030003e30001005f6000e100025f5fe4",
                EOFException.STACK_UNDERFLOW,
                id="retf_underflow_b",
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
