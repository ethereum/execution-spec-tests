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
                  name="EOFV1_0001",
                  raw_bytes=(
                      [
                          0xef,
                          0x00,
                          0x01,
                          0x01,
                          0x00,
                          0x04,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x05,
                          0x03,
                          0x00,
                          0x01,
                          0x00,
                          0x14,
                          0x04,
                          0x00,
                          0x00,
                          0x00,
                          0x00,
                          0x80,
                          0x00,
                          0x04,
                          0x60,
                          0x00,
                          0x60,
                          0x00,
                          0xee,
                          0xef,
                          0x00,
                          0x01,
                          0x01,
                          0x00,
                          0x04,
                          0x02,
                          0x00,
                          0x01,
                          0x00,
                          0x01,
                          0x04,
                          0x00,
                          0x00,
                          0x00,
                          0x00,
                          0x80,
                          0x00,
                          0x00,
                          0xfe,
                      ]),
              ),
              "ef000101000402000100050300010014040000000080000460006000eeef000101000402000100010400000000800000fe",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_returncontract_invalid_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURNCONTRACT[1], max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0002_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
                kind=ContainerKind.INITCODE
              )
              ,
              "ef000101000402000100060300010014040000000080000460006000ee01ef000101000402000100010400000000800000fe",
              EOFException.INVALID_CONTAINER_SECTION_INDEX,
              id="eof1_returncontract_invalid_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURNCONTRACT[255], max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0003_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
                kind=ContainerKind.INITCODE
              )
              ,
              "ef000101000402000100060300010014040000000080000460006000eeffef000101000402000100010400000000800000fe",
              EOFException.INVALID_CONTAINER_SECTION_INDEX,
              id="eof1_returncontract_invalid_2"
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
