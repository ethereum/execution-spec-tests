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
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[0] + Op.PUSH1[0x01] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000904000000008000016000e2000000600100",
                None,
                id="single_entry_case_0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x00] + Op.RJUMPV[0,3] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000016000e20100000003600100600200",
                None,
                id="two_entries_case_0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000e04000000008000016002e20100000003600100600200",
                None,
                id="two_entries_case_2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x02] + Op.RJUMPV[0,3,-10] + Op.PUSH1[0x01] + Op.STOP + Op.PUSH1[0x02] + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001004000000008000016002e20200000003fff6600100600200",
                None,
                id="three_entries_case_2",
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
