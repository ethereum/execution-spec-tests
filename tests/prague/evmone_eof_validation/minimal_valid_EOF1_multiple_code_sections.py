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
                raw_bytes=bytes(
                     [
                        0xef,
                        0x00,
                        0x01,
                        0x01,
                        0x00,
                        0x08,
                        0x02,
                        0x00,
                        0x02,
                        0x00,
                        0x01,
                        0x00,
                        0x01,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0x00,
                        0x80,
                        0x00,
                        0x00,
                        0xfe,
                        0xfe,

                     ]),
                ),
                "0xef000101000802000200010001000080000000800000fefe",
                EOFException.MISSING_DATA_SECTION,
                id="no_data_section",
            ),
            
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.JUMPF[0x0001], max_stack_height=0),
						Section.Code(code=Op.INVALID, max_stack_height=0),
						Section.Data(data="da"),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200030001040001000080000000800000e50001feda",
                None,
                id="with_data_section",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH0 + Op.CALLF[0x0001] + Op.STOP, max_stack_height=1),
						Section.Code(code=Op.POP + Op.CALLF[0x0002] + Op.POP + Op.RETF, code_inputs=1, code_outputs=0, max_stack_height=1),
						Section.Code(code=Op.ADDRESS + Op.DUP1 + Op.CALLF[0x0003] + Op.POP * 2 + Op.RETF, code_outputs=1, max_stack_height=3),
						Section.Code(code=Op.DUP1 + Op.RETF, code_inputs=2, code_outputs=3, max_stack_height=3),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010010020004000500060008000204000000008000010100000100010003020300035fe300010050e3000250e43080e300035050e480e4",
                None,
                id="non_void_input_output",
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
