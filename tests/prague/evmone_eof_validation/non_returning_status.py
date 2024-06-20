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
                        Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010001040000000080000000",
                None,
                id="non_returning_no_jumpf_no_retf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.STOP, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030001040000000080000000800000e5000100",
                None,
                id="non_returning_jumpf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=0),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040001040000000080000000000000e3000100e4",
                None,
                id="returning_retf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0002], code_outputs=0, max_stack_height=0),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040003000104000000008000000000000000000000e3000100e50002e4",
                None,
                id="returning_jumpf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.RJUMPI[0x0001] + Op.RETF + Op.JUMPF[0x0002], code_inputs=1, code_outputs=0, max_stack_height=1),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c020003000500070001040000000080000101000001000000005fe3000100e10001e4e50002e4",
                None,
                id="returning_jumpf_returning_retf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.RJUMPI[0x0001] + Op.RETF + Op.JUMPF[0x0000], code_inputs=1, code_outputs=0, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000500070400000000800001010000015fe3000100e10001e4e50000",
                None,
                id="returning_retf_non_returning_jumpf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.RETF, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030001040000000080000000800000e50001e4",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_retf_on_non_returning_function_a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.RETF, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000e4",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_retf_on_non_returning_function_b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0002], max_stack_height=0),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300030003000104000000008000000080000000000000e50001e50002e4",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_jumpf_to_returning_function",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0000], code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030003040000000080000000000000e50001e50000",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_jumpf_to_non_returning_function",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.JUMPF[0x0001], max_stack_height=1),
						Section.Code(code=Op.RJUMPI[0x0001] + Op.RETF + Op.JUMPF[0x0002], code_inputs=1, max_stack_height=1),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c020003000400070001040000000080000101800001000000005fe50001e10001e4e50002e4",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_jumpf_to_returning_function_retf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.JUMPF[0x0001], max_stack_height=1),
						Section.Code(code=Op.RJUMPI[0x0001] + Op.RETF + Op.JUMPF[0x0000], code_inputs=1, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000400070400000000800001018000015fe50001e10001e4e50000",
                EOFException.INVALID_NON_RETURNING_FLAG,
                id="invalid_jumpf_to_non_returning_function_retf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0002], max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300030003000304000000008000000080000000800000e50001e50002e50001",
                None,
                id="circular_jumpf_non_returning",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00014",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0002], code_outputs=0, max_stack_height=0),
						Section.Code(code=Op.JUMPF[0x0001], code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000c02000300040003000304000000008000000000000000000000e3000100e50002e50001",
                None,
                id="circular_jumpf_returning",
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
