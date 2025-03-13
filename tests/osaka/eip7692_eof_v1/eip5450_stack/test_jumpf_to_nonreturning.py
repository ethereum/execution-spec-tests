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
            name="jumpf_to_nonreturning_0",
            sections=[
                Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=2),
                Section.Code(code=Op.STOP),
            ],
            expected_bytecode="ef0001010008020002000500010400000000800002008000005f5fe5000100",
        ),
        Container(
            name="jumpf_to_nonreturning_1",
            sections=[
                Section.Code(code=Op.PUSH0 * 3 + Op.JUMPF[1], max_stack_height=3),
                Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
            ],
            expected_bytecode="ef0001010008020002000600010400000000800003038000035f5f5fe5000100",
        ),
        Container(
            name="jumpf_to_nonreturning_2",
            sections=[
                Section.Code(code=Op.PUSH0 * 4 + Op.JUMPF[1], max_stack_height=4),
                Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
            ],
            expected_bytecode="ef0001010008020002000700010400000000800004038000035f5f5f5fe5000100",
        ),
        Container(
            name="jumpf_to_nonreturning_3",
            sections=[
                Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[1], max_stack_height=2),
                Section.Code(code=Op.STOP, code_inputs=3, max_stack_height=3),
            ],
            expected_bytecode="ef0001010008020002000500010400000000800002038000035f5fe5000100",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_jumpf_to_nonreturning(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test JUMPF to non-returning function."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
