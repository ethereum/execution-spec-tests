""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section, ContainerKind

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "7a664ec21843615efde4dae03205758f6569cdb7"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURN, max_stack_height=2),
                    ],
                kind=ContainerKind.INITCODE
              )
              ,
              "ef00010100040200010005040000000080000260006000f3",
              EOFException.INCOMPATIBLE_CONTAINER_KIND,
              id="initcode_container_return_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0002_D1I0',
                        sections = [
                            Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURN, max_stack_height=2),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000b030001001804000000008000046000600060006000ec0000ef00010100040200010005040000000080000260006000f3",
              EOFException.INCOMPATIBLE_CONTAINER_KIND,
              id="initcode_container_return_1"
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
