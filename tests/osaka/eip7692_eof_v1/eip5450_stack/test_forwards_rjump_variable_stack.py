"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="forwards_rjump_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.RJUMP[0]
                    + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000035f6000e100025f5fe0000000",
        ),
        Container(
            name="forwards_rjump_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.PUSH1[0]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[1]
                    + Op.NOT
                    + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e10003e000011900",
        ),
        Container(
            name="forwards_rjump_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.PUSH1[0]
                    + Op.RJUMPI[8]
                    + Op.PUSH1[0]
                    + Op.RJUMPI[6]
                    + Op.RJUMP[4]
                    + Op.RJUMP[1]
                    + Op.NOT
                    + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000055f6000e100025f5f5f6000e100086000e10006e00004e000011900",
        ),
        Container(
            name="forwards_rjump_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 3
                    + Op.PUSH1[0]
                    + Op.RJUMPI[3]
                    + Op.RJUMP[1]
                    + Op.PUSH0
                    + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e10003e000015f00",
        ),
        Container(
            name="forwards_rjump_variable_stack_4",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH1[0]
                    + Op.RJUMPI[2]
                    + Op.PUSH0 * 2
                    + Op.PUSH1[0]
                    + Op.RJUMPI[8]
                    + Op.PUSH1[0]
                    + Op.RJUMPI[7]
                    + Op.RJUMP[5]
                    + Op.PUSH0
                    + Op.RJUMP[1]
                    + Op.NOT
                    + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000045f6000e100025f5f6000e100086000e10007e000055fe000011900",
        ),
    ],
    ids=lambda c: c.name,
)
def test_forwards_rjump_variable_stack(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test forwards RJUMP (variable stack)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
