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
                        Section.Code(code=Op.RJUMP[0xfffd], max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100030400000000800000e0fffd",
                None,
                id="rjump",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPI[0xfffd] + Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000604000000008000006000e1fffd00",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="rjumpi",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[-4] + Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000704000000008000006000e200fffc00",
                EOFException.STACK_HEIGHT_MISMATCH,
                id="rjumpv",
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
