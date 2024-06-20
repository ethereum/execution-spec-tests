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
                        Section.Code(code=Op.PUSH0 + Op.RJUMPI[0x0007] + Op.PUSH0 * 3 + Op.RJUMPI[0x0001] + Op.POP + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000045fe100075f5f5fe10001505f5ffd",
                None,
                id="non_constant_stack_height_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 2 + Op.RJUMPI[0x0007] + Op.PUSH0 * 3 + Op.RJUMPI[0x0001] + Op.POP + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=5),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f04000000008000055f5fe100075f5f5fe10001505f5ffd",
                None,
                id="non_constant_stack_height_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.RJUMPI[0x0007] + Op.PUSH0 * 3 + Op.RJUMPI[0x0001] + Op.POP * 2 + Op.PUSH0 * 2 + Op.REVERT, max_stack_height=4),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000f04000000008000045fe100075f5f5fe1000150505f5ffd",
                EOFException.STACK_UNDERFLOW,
                id="non_constant_stack_height_3",
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
