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
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.INVALID, code_inputs=5, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00010400000000800003058000055f6000e100025f5fe50001fe",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_nonreturning_variable_stack_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.INVALID, code_inputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00010400000000800003038000035f6000e100025f5fe50001fe",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_nonreturning_variable_stack_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.INVALID, code_inputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00010400000000800003018000015f6000e100025f5fe50001fe",
                None,
                id="jumpf_to_nonreturning_variable_stack_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.PUSH1[0x00] + Op.RJUMPI[0x0002] + Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.INVALID, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000b00010400000000800003008000005f6000e100025f5fe50001fe",
                None,
                id="jumpf_to_nonreturning_variable_stack_4",
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
