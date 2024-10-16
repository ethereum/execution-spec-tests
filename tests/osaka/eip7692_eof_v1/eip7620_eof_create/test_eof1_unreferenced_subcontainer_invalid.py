""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "7a664ec21843615efde4dae03205758f6569cdb7"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.STOP, max_stack_height=0),
                    Section.Container(container=Container(
                        name = 'EOFV1_0001_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef000101000402000100010300010014040000000080000000ef000101000402000100010400000000800000fe",
              EOFException.ORPHAN_SUBCONTAINER,
              id="eof1_unreferenced_subcontainer_invalid_0"
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
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
