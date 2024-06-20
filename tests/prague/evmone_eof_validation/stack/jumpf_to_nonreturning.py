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
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030001040000000080000000800000e5000100",
                None,
                id="jumpf_to_nonreturning_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=2),
						Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000500010400000000800002008000005f5fe5000100",
                None,
                id="jumpf_to_nonreturning_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[0x0001], max_stack_height=3),
						Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000600010400000000800003038000035f5f5fe5000100",
                None,
                id="jumpf_to_nonreturning_3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[0x0001], max_stack_height=4),
						Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000700010400000000800004038000035f5f5f5fe5000100",
                None,
                id="jumpf_to_nonreturning_4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[0x0001], max_stack_height=2),
						Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000500010400000000800002038000035f5fe5000100",
                EOFException.STACK_UNDERFLOW,
                id="jumpf_to_nonreturning_5",
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
