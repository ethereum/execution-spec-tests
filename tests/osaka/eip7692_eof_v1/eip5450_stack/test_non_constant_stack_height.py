"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="non_constant_stack_height_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000045fe100075f5f5fe10001505f5ffd",
        ),
        Container(
            name="non_constant_stack_height_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 2
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000055f5fe100075f5f5fe10001505f5ffd",
        ),
        Container(
            name="non_constant_stack_height_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP * 2
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000045fe100075f5f5fe1000150505f5ffd",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_non_constant_stack_height(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test code sections reachable with different stack heights."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
