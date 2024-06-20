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
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040003040000000080000200020002e30001005f5fe4",
                None,
                id="retf_stack_validation_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=2, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040002040000000080000200020001e30001005fe4",
                EOFException.STACK_UNDERFLOW,
                id="retf_stack_validation_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 3 + Op.RETF, code_outputs=2, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="retf_stack_validation_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.RJUMPI[0x0007] + Op.PUSH1[0x01] * 2 + Op.RJUMP[0x0002] + Op.PUSH0 * 2 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
                None,
                id="retf_stack_validation_4",
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
