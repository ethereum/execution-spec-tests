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
                        Section.Code(code=Op.DATALOADN[0x0000] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400200000800001d1000050000000000000000000111111111111111122222222222222223333333333333333",
                None,
                id="dataloadn_correct_index_0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0001] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="000000000000000011111111111111112222222222222222333333333333333344"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400210000800001d100015000000000000000000011111111111111112222222222222222333333333333333344",
                None,
                id="dataloadn_correct_index_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0020] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="00000000000000001111111111111111222222222222222233333333333333330000000000000000111111111111111122222222222222223333333333333333"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400400000800001d10020500000000000000000001111111111111111222222222222222233333333333333330000000000000000111111111111111122222222222222223333333333333333",
                None,
                id="dataloadn_correct_index_32",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0000] + Op.POP + Op.STOP, max_stack_height=1),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400000000800001d100005000",
                EOFException.INVALID_DATALOADN_INDEX,
                id="dataloadn_no_data_section",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0001] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="00"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400010000800001d10001500000",
                EOFException.INVALID_DATALOADN_INDEX,
                id="dataloadn_out_of_bounds_index_1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0020] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400200000800001d1002050000000000000000000111111111111111122222222222222223333333333333333",
                EOFException.INVALID_DATALOADN_INDEX,
                id="dataloadn_out_of_bounds_index_32",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0xffff] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100050400200000800001d1ffff50000000000000000000111111111111111122222222222222223333333333333333",
                EOFException.INVALID_DATALOADN_INDEX,
                id="dataloadn_out_of_bounds_index_uint16_max",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.DATALOADN[0x0020] + Op.POP + Op.STOP, max_stack_height=1),
						Section.Data(data="000000000000000011111111111111112222222222222222333333333333333300000000000000001111111111111111222222222222222233333333333333"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001000504003f0000800001d100205000000000000000000011111111111111112222222222222222333333333333333300000000000000001111111111111111222222222222222233333333333333",
                EOFException.INVALID_DATALOADN_INDEX,
                id="dataloadn_truncated_word_index_32",
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
