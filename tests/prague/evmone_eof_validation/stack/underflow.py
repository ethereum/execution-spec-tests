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
                        Section.Code(code=Op.ADD + Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000204000000008000000100",
                EOFException.STACK_UNDERFLOW,
                id="underflow_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040002040000000080000101020002e30001005fe4",
                EOFException.STACK_UNDERFLOW,
                id="callf_underflow",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.JUMPF[0x0002], code_outputs=2, max_stack_height=0),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_inputs=1, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040003000204000000008000020002000001020002e3000100e500025fe4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_returning_function",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.PUSH1[0x00] * 2 + Op.REVERT, code_inputs=1, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030005040000000080000001800003e5000160006000fd",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_non_returning_function",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=2, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040002040000000080000200020001e30001005fe4",
                EOFException.STACK_UNDERFLOW,
                id="retf_underflow",
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
