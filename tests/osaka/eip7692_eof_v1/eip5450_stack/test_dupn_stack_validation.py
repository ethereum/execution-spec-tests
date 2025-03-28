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
            name="dupn_stack_validation_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[0] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e60000",
        ),
        Container(
            name="dupn_stack_validation_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[19] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e61300",
        ),
        Container(
            name="dupn_stack_validation_2",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[20] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e61400",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="dupn_stack_validation_3",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[208] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6d000",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="dupn_stack_validation_4",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[254] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6fe00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="dupn_stack_validation_5",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 20 + Op.DUPN[255] + Op.STOP,
                    max_stack_height=21,
                ),
            ],
            expected_bytecode="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6ff00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_dupn_stack_validation(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test DUPN stack validation."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
