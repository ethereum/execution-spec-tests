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
            name="ambiguous_container_kind_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.PUSH1[0] * 2 + Op.RETURNCODE[0],
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="ambiguous_container_kind_0_D1I0",
                        sections=[
                            Section.Code(code=Op.INVALID),
                        ],
                    )
                ),
                Section.Container(
                    container=Container(
                        name="ambiguous_container_kind_0_D1I1",
                        sections=[
                            Section.Code(code=Op.INVALID),
                        ],
                    )
                ),
            ],
            kind=ContainerKind.INITCODE,
            expected_bytecode="ef000101000402000100100300020014001404000000008000046000600060006000ec0060006000ee00ef000101000402000100010400000000800000feef000101000402000100010400000000800000fe",
            validity_error=[EOFException.AMBIGUOUS_CONTAINER_KIND],
        ),
        Container(
            name="eofcreate_return_and_returncontract_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="eofcreate_return_and_returncontract_0_D1I0",
                        sections=[
                            Section.Code(
                                code=Op.PUSH1[0]
                                + Op.RJUMPI[5]
                                + Op.PUSH1[0] * 2
                                + Op.RETURN
                                + Op.PUSH1[0] * 2
                                + Op.RETURNCODE[0],
                                max_stack_height=2,
                            ),
                            Section.Container(
                                container=Container(
                                    name="eofcreate_return_and_returncontract_0_D2I0",
                                    sections=[
                                        Section.Code(code=Op.INVALID),
                                    ],
                                )
                            ),
                        ],
                    )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001003c04000000008000046000600060006000ec0000ef00010100040200010010030001001404000000008000026000e1000560006000f360006000ee00ef000101000402000100010400000000800000fe",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
        Container(
            name="eofcreate_stop_and_returncontract_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[0] * 4 + Op.EOFCREATE[0] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Container(
                    container=Container(
                        name="eofcreate_stop_and_returncontract_0_D1I0",
                        sections=[
                            Section.Code(
                                code=Op.PUSH1[0]
                                + Op.RJUMPI[1]
                                + Op.STOP
                                + Op.PUSH1[0] * 2
                                + Op.RETURNCODE[0],
                                max_stack_height=2,
                            ),
                            Section.Container(
                                container=Container(
                                    name="eofcreate_stop_and_returncontract_0_D2I0",
                                    sections=[
                                        Section.Code(code=Op.INVALID),
                                    ],
                                )
                            ),
                        ],
                    )
                ),
            ],
            expected_bytecode="ef0001010004020001000b030001003804000000008000046000600060006000ec0000ef0001010004020001000c030001001404000000008000026000e100010060006000ee00ef000101000402000100010400000000800000fe",
            validity_error=[EOFException.INCOMPATIBLE_CONTAINER_KIND],
        ),
    ],
    ids=lambda c: c.name,
)
def test_same_eofcreate_and_returncontract_target(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test ambiguous container targets."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
