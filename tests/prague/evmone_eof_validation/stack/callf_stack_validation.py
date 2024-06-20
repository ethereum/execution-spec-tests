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
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.PUSH0 * 2 + Op.CALLF[0x0002] + Op.RETF, code_outputs=1, max_stack_height=2),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040006000204000000008000010001000202010002e30001005f5fe30002e450e4",
                None,
                id="callf_stack_validation_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.PUSH0 * 3 + Op.CALLF[0x0002] + Op.RETF, code_outputs=1, max_stack_height=3),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040007000204000000008000010001000302010002e30001005f5f5fe30002e450e4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="callf_stack_validation_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.PUSH0 + Op.CALLF[0x0002] + Op.RETF, code_outputs=1, max_stack_height=1),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=2, code_outputs=1, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040005000204000000008000010001000102010002e30001005fe30002e450e4",
                EOFException.STACK_UNDERFLOW,
                id="callf_stack_validation_3",
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
