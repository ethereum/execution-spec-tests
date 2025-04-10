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
            name="exchange_deep_stack_validation_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 33 + Op.EXCHANGE[255] + Op.STOP,
                    max_stack_height=33,
                ),
            ],
            expected_bytecode="ef000101000402000100450400000000800021600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001600160016001e8ff00",
        ),
        Container(
            name="exchange_stack_validation_0",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[0] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80000",
        ),
        Container(
            name="exchange_stack_validation_1",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[16] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81000",
        ),
        Container(
            name="exchange_stack_validation_2",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[1] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80100",
        ),
        Container(
            name="exchange_stack_validation_3",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[32] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e82000",
        ),
        Container(
            name="exchange_stack_validation_4",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[2] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80200",
        ),
        Container(
            name="exchange_stack_validation_5",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[112] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87000",
        ),
        Container(
            name="exchange_stack_validation_6",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[7] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80700",
        ),
        Container(
            name="exchange_stack_validation_7",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[17] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81100",
        ),
        Container(
            name="exchange_stack_validation_8",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[52] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83400",
        ),
        Container(
            name="exchange_stack_validation_9",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[67] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84300",
        ),
        Container(
            name="exchange_stack_validation_10",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[22] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81600",
        ),
        Container(
            name="exchange_stack_validation_11",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[97] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e86100",
        ),
        Container(
            name="exchange_stack_validation_12",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[128] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e88000",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_13",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[8] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e80800",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_14",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[113] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e87100",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_15",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[23] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e81700",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_16",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[68] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e84400",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_17",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[83] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e85300",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_18",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[53] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e83500",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_19",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[238] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ee00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_20",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[239] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ef00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_21",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[254] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8fe00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
        Container(
            name="exchange_stack_validation_22",
            sections=[
                Section.Code(
                    code=Op.PUSH1[1] * 10 + Op.EXCHANGE[255] + Op.STOP,
                    max_stack_height=10,
                ),
            ],
            expected_bytecode="ef00010100040200010017040000000080000a6001600160016001600160016001600160016001e8ff00",
            validity_error=[EOFException.STACK_UNDERFLOW],
        ),
    ],
    ids=lambda c: c.name,
)
def test_exchange_deep_stack_validation(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EXCHANGE (deep stack)."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
