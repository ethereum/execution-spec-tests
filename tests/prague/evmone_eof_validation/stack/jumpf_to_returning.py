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
						Section.Code(code=Op.JUMPF[0x0002], code_outputs=2, max_stack_height=0),
						Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040003000304000000008000020002000000020002e3000100e500025f5fe4",
                None,
                id="jumpf_to_returning_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 2 + Op.RETF, code_outputs=2, max_stack_height=2),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040005000304000000008000020002000200020002e30001005f5fe500025f5fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040006000204000000008000020002000303020003e30001005f5f5fe5000250e4",
                None,
                id="jumpf_to_returning_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=4),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040007000204000000008000020002000403020003e30001005f5f5f5fe5000250e4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=2),
						Section.Code(code=Op.POP + Op.RETF, code_inputs=3, code_outputs=2, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040005000204000000008000020002000203020003e30001005f5fe5000250e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=1),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040004000204000000008000020002000100010001e30001005fe500025fe4",
                None,
                id="jumpf_to_returning_6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040006000204000000008000020002000300010001e30001005f5f5fe500025fe4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.JUMPF[0x0002], code_outputs=2, max_stack_height=0),
						Section.Code(code=Op.PUSH0 + Op.RETF, code_outputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040003000204000000008000020002000000010001e3000100e500025fe4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=4),
						Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040007000304000000008000020002000403010003e30001005f5f5f5fe500025050e4",
                None,
                id="jumpf_to_returning_9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 5 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=5),
						Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040008000304000000008000020002000503010003e30001005f5f5f5f5fe500025050e4",
                EOFException.STACK_HIGHER_THAN_OUTPUTS,
                id="jumpf_to_returning_10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=2),
						Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[0x0002], code_outputs=2, max_stack_height=3),
						Section.Code(code=Op.POP * 2 + Op.RETF, code_inputs=3, code_outputs=1, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040006000304000000008000020002000303010003e30001005f5f5fe500025050e4",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_returning_11",
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
