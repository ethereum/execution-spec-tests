"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFTestFiller, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"


# Max number (256) of container sections
bytecode = None
for i in range(0, 256):
    if bytecode:
        bytecode += Op.PUSH1[0] * 4 + Op.EOFCREATE[i] + Op.POP
    else:
        bytecode = Op.PUSH1[0] * 4 + Op.EOFCREATE[i] + Op.POP
bytecode += Op.STOP

code = Section.Code(code=bytecode)
subcontainer = Container(
    name="EOFV1_MINCONTAINER",
    sections=[
        Section.Code(code=Op.INVALID),
    ],
)

eof1_embedded_container_6 = Container(
    name="contract_with_embedded_container_6",
    sections=[code] + [Section.Container(container=subcontainer)] * 256,
)

@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="contract_with_embedded_container_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[2] + Op.PUSH1[0] + Op.RETURNCODE[0],
                    max_stack_height=2,
                ),
                Section.Container(
                    container=Container(
                      name="contract_with_embedded_container_0_D1I0",
                      sections=[
                          Section.Code(code=Op.INVALID),
                          Section.Data(data="", custom_size=2),
                      ],
                  )
                ),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef000101000402000100060300010014040000000080000260026000ee00ef000101000402000100010400020000800000fe",
        ),
        Container(
            name="contract_with_embedded_container_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] + Op.PUSH1[0] + Op.RETURNCODE[0],
                    max_stack_height=2,
                ),
                Section.Container(
                    container=Container(
                      name="contract_with_embedded_container_1_D1I0",
                      sections=[
                          Section.Code(code=Op.INVALID),
                          Section.Data(data="aa", custom_size=2),
                      ],
                  )
                ),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef000101000402000100060300010015040000000080000260016000ee00ef000101000402000100010400020000800000feaa",
        ),
        Container(
            name="contract_with_embedded_container_2",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                      name="contract_with_embedded_container_2_D1I0",
                      sections=[
                          Section.Code(code=Op.INVALID),
                      ],
                  )
                ),
            Section.Data(data="aabb"),
                ],
            expected_bytecode="ef0001010004020001000b030001001404000200008000046000600060006000ec0000ef000101000402000100010400000000800000feaabb",
        ),
        Container(
            name="contract_with_embedded_container_3",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4
                    + Op.EOFCREATE[0]
                    + Op.POP
                    + Op.PUSH1[0] * 4
                    + Op.EOFCREATE[1]
                    + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                      name="contract_with_embedded_container_3_D1I0",
                      sections=[
                          Section.Code(code=Op.INVALID),
                      ],
                  )
                ),
            Section.Container(
                    container=Container(
                      name="contract_with_embedded_container_3_D1I1",
                      sections=[
                          Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, max_stack_height=2),
                      ],
                  )
                ),
            ],
            expected_bytecode="ef000101000402000100160300020014001804000000008000046000600060006000ec00506000600060006000ec0100ef000101000402000100010400000000800000feef00010100040200010005040000000080000260006000fd",
        ),
        eof1_embedded_container_6,
    ],
    ids=lambda c: c.name,
)
def test_embedded_container(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contract with subcontainers."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
