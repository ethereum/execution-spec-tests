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
                        Section.Code(code=Op.PUSH0 * 127 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=127),
						Section.Code(code=Op.RETF, code_inputs=127, code_outputs=127, max_stack_height=127),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200830001040000000080007f7f7f007f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5fe3000100e4",
                None,
                id="valid_127_inputs_127_outputs",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=0),
						Section.Code(code=Op.RETF, code_inputs=128, max_stack_height=128),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040001040000000080000080800080e3000100e4",
                EOFException.INPUTS_OUTPUTS_NUM_ABOVE_LIMIT,
                id="invalid_128_inputs_128_outputs",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=127),
						Section.Code(code=Op.PUSH1[0x01] * 127 + Op.RETF, code_outputs=127, max_stack_height=127),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010008020002000400ff040000000080007f007f007fe30001006001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001e4",
                None,
                id="valid_127_outputs",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=129),
						Section.Code(code=Op.PUSH1[0x01] * 129 + Op.RETF, code_outputs=129, max_stack_height=129),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040103040000000080008100810081e3000100600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001e4",
                EOFException.INPUTS_OUTPUTS_NUM_ABOVE_LIMIT,
                id="invalid_129_outputs",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH0 * 127 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=127),
						Section.Code(code=Op.POP * 127 + Op.RETF, code_inputs=127, code_outputs=0, max_stack_height=127),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200830080040000000080007f7f00007f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5fe300010050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050e4",
                None,
                id="valid_127_inputs",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] * 128 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=128),
						Section.Code(code=Op.POP * 128 + Op.RETF, code_inputs=128, code_outputs=0, max_stack_height=128),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100080200020104008104000000008000808000008060016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001e30001005050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050505050e4",
                EOFException.INPUTS_OUTPUTS_NUM_ABOVE_LIMIT,
                id="invalid_128_inputs",
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
