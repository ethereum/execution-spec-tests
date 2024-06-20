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
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=5, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000204000000008000030003000305030003e30001005f6000e100025f5fe500025fe4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.RETF, code_inputs=3, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000104000000008000030003000303030003e30001005f6000e100025f5fe50002e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_inputs=1, code_outputs=3, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000304000000008000030003000301030005e30001005f6000e100025f5fe500025f5fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_variable_stack_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=3, max_stack_height=3),
						Section.Code(code=Op.PUSH0 * 3 + Op.RETF, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000404000000008000030003000300030003e30001005f6000e100025f5fe500025f5f5fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_variable_stack_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.POP * 4 + Op.RETF, code_inputs=5, code_outputs=1, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000504000000008000020002000305010005e30001005f6000e100025f5fe5000250505050e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_variable_stack_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000304000000008000020002000303010003e30001005f6000e100025f5fe500025050e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_variable_stack_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.RETF, code_inputs=1, code_outputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000104000000008000020002000301010001e30001005f6000e100025f5fe50002e4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_variable_stack_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c0200030004000b000204000000008000020002000300010001e30001005f6000e100025f5fe500025fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_variable_stack_8",
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
