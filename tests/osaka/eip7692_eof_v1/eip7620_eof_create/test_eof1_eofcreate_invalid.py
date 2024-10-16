""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section, ContainerKind

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "7a664ec21843615efde4dae03205758f6569cdb7"

# Truncated EOFCREATE at the end
eof1_eofcreate_invalid_0 = Container(
    name="EOFV1_0001",
    sections=[
        Section.Code(code=Op.PUSH1[0] + Op.PUSH1[0xff] + Op.PUSH1[0] * 2 + Op.EOFCREATE),
        Section.Container(container=Container(name="EOFV1_MINCONTAINER", sections=[Section.Code(code=Op.INVALID)])),
    ],
    kind=ContainerKind.RUNTIME,
)


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              eof1_eofcreate_invalid_0,
              "ef0001010004020001000903000100140400000000800004600060ff60006000ecef000101000402000100010400000000800000fe",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_eofcreate_invalid_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[0], max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0002_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000a03000100140400000000800004600060ff60006000ec00ef000101000402000100010400000000800000fe",
              EOFException.MISSING_STOP_OPCODE,
              id="eof1_eofcreate_invalid_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[1] + Op.POP + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0003_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000c03000100140400000000800004600060ff60006000ec015000ef000101000402000100010400000000800000fe",
              EOFException.INVALID_CONTAINER_SECTION_INDEX,
              id="eof1_eofcreate_invalid_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[255] + Op.POP + Op.STOP, max_stack_height=4),
                    Section.Container(container=Container(
                        name = 'EOFV1_0004_D1I0',
                        sections = [
                            Section.Code(code=Op.INVALID, max_stack_height=0),
                            ],
                      )
                    ),  
                ],
              )
              ,
              "ef0001010004020001000c03000100140400000000800004600060ff60006000ecff5000ef000101000402000100010400000000800000fe",
              EOFException.INVALID_CONTAINER_SECTION_INDEX,
              id="eof1_eofcreate_invalid_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.PUSH1[255] + Op.PUSH1[0] * 2 + Op.EOFCREATE[0] + Op.POP + Op.STOP, max_stack_height=4),
                    Section.Container(
                         container=Container(
                             name="EOFV1_0001",
                             raw_bytes=(
                               [
                                 0xef, 0x00, 0x01, # Version: 1
                                 0x01, 0x00, 0x04, # Types Length: 4
                                 0x02, 0x00, 0x01, # Code Sections (Length: 1)
                                       0x00, 0x01, #   Code Section 0 (Length: 1)
                                 0x04, 0x00, 0x03, # Data Length: 3
                                             0x00, # Terminator
                                                   # Code Section 0 types
                                             0x00, #   Inputs: 0
                                             0x80, #   Outputs: 0 (Non-returning function)
                                       0x00, 0x00, #   Max Stack Height: 0
                                 
                                                   # Code Section 0
                                             0xfe, #  [0] INVALID 
                                                   # Data Section (Truncated: 2 != 3)
                                 0xaa,
                                 0xbb
                               ]),
                         )
                     ),
              					      
                ],
              )
              ,
              "ef0001010004020001000c03000100160400000000800004600060ff60006000ec005000ef000101000402000100010400030000800000feaabb",
              EOFException.EOF_CREATE_WITH_TRUNCATED_CONTAINER,
              id="eof1_eofcreate_invalid_4"
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
