""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "7a664ec21843615efde4dae03205758f6569cdb7"

min_container = Container(
    name="EOFV1_MINCONTAINER",
    sections=[
        Section.Code(code=Op.INVALID),
    ]
)

invalid_subcontainer_0 = bytes(min_container) + b"\xde\xad\xbe\xef" # Add some trailing bytes

eof1_trailing_bytes_in_subcontainer_0 = Container(
    name="EOFV1_0000",
    sections=[
        Section.Code(Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
        Section.Container(container=Container(name="EOFV1_0000_D1I0", raw_bytes=invalid_subcontainer_0)),
    ],
)

min_container_with_data = Container(
    name="EOFV1_MINCONTAINER",
    sections=[
        Section.Code(code=Op.INVALID),
        Section.Data(data="aabb"),
    ]
)

invalid_subcontainer_1 = bytes(min_container_with_data) + b"\xde\xad\xbe\xef" # Add some trailing bytes

eof1_trailing_bytes_in_subcontainer_1 = Container(
        name="EOFV1_0001",
        sections=[
            Section.Code(Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP, max_stack_height=4),
            Section.Container(container=Container(name="EOFV1_0001_D1I0", raw_bytes=invalid_subcontainer_1)),
        ],
)


@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              eof1_trailing_bytes_in_subcontainer_0,
              "ef0001010004020001000b030001001804000000008000046000600060006000ec0000ef000101000402000100010400000000800000fedeadbeef",
              EOFException.INVALID_SECTION_BODIES_SIZE,
              id="eof1_trailing_bytes_in_subcontainer_0"
        ),
        pytest.param(
              eof1_trailing_bytes_in_subcontainer_1,
              "ef0001010004020001000b030001001a04000000008000046000600060006000ec0000ef000101000402000100010400020000800000feaabbdeadbeef",
              EOFException.INVALID_SECTION_BODIES_SIZE,
              id="eof1_trailing_bytes_in_subcontainer_1"
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
