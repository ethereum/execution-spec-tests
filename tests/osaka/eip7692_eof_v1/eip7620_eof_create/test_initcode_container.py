"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="initcode_container_return_0",
            sections=[
                Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURN, max_stack_height=2),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef00010100040200010005040000000080000260006000f3",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
        Container(
            name="initcode_container_return_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="initcode_container_return_1_D1I0",
                        sections=[
                            Section.Code(code=Op.PUSH1[0] * 2 + Op.RETURN, max_stack_height=2),
                        ],
                    )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001001804000000008000046000600060006000ec0000ef00010100040200010005040000000080000260006000f3",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
        Container(
            name="initcode_container_revert_0",
            sections=[
                Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, max_stack_height=2),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef00010100040200010005040000000080000260006000fd",
        ),
        Container(
            name="initcode_container_revert_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="initcode_container_revert_1_D1I0",
                        sections=[
                            Section.Code(code=Op.PUSH1[0] * 2 + Op.REVERT, max_stack_height=2),
                        ],
                    )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001001804000000008000046000600060006000ec0000ef00010100040200010005040000000080000260006000fd",
        ),
        Container(
            name="initcode_container_stop_0",
            sections=[
                Section.Code(code=Op.STOP),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef00010100040200010001040000000080000000",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
        Container(
            name="initcode_container_stop_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="initcode_container_stop_1_D1I0",
                        sections=[
                            Section.Code(code=Op.STOP),
                        ],
                    )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001001404000000008000046000600060006000ec0000ef00010100040200010001040000000080000000",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
    ],
    ids=lambda c: c.name,
)
def test_initcode_container_return(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test initcode container with RETURN instruction."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
