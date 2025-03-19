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
            name="swapn_stack_validation_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[0] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e70000",
        ),
        Container(
            name="swapn_stack_validation_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[18] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e71200",
        ),
        Container(
            name="swapn_stack_validation_2",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[19] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e71300",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="swapn_stack_validation_3",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[208] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7d000",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="swapn_stack_validation_4",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[254] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7fe00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="swapn_stack_validation_5",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.SWAPN[255] + Op.STOP,
                    max_stack_height=20,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001460016001600160016001600160016001600160016001600160016001600160016001600160016001e7ff00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_swapn_stack_validation(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test SWAPN stack validation."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
