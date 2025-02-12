"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "f20b164b00ae5553f7536a6d7a83a0f254455e09"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="backwards_rjumpi_0",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] +
                    Op.RJUMPI[-7] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000804000000008000015f506000e1fff900",
          ),
        Container(
            name="backwards_rjumpi_1",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] +
                    Op.RJUMPI[-7] + Op.PUSH1[0] + Op.RJUMPI[-12] +
                    Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000015f506000e1fff96000e1fff400",
          ),
        Container(
            name="backwards_rjumpi_2",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] +
                    Op.RJUMPI[-7] + Op.PUSH0 + Op.PUSH1[0] +
                    Op.RJUMPI[-13] + Op.STOP,
                    max_stack_height=2),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000025f506000e1fff95f6000e1fff300",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_3",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[1] + Op.ADD + Op.DUP1 +
                    Op.RJUMPI[-7] + Op.STOP,
                    max_stack_height=2),
            ],
            expected_bytecode="ef0001010004020001000904000000008000025f60010180e1fff900",
          ),
        Container(
            name="backwards_rjumpi_4",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[1] + Op.ADD + Op.DUP1 * 2 +
                    Op.RJUMPI[-8] + Op.STOP,
                    max_stack_height=2),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000025f6001018080e1fff800",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_5",
            sections=[
                Section.Code(code=Op.PUSH0 * 3 + Op.POP + Op.RJUMPI[-4] +
                    Op.STOP,
                    max_stack_height=2),
            ],
            expected_bytecode="ef0001010004020001000804000000008000025f5f5f50e1fffc00",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_6",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] +
                    Op.RJUMPI[-7] + Op.RJUMP[-10],
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000015f506000e1fff9e0fff6",
          ),
        Container(
            name="backwards_rjumpi_7",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.POP + Op.PUSH1[0] +
                    Op.RJUMPI[-7] + Op.PUSH0 + Op.RJUMP[-11],
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000015f506000e1fff95fe0fff5",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_8",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] +
                    Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[-11] +
                    Op.STOP,
                    max_stack_height=3),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000035f6000e100015f6000e1fff500",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_9",
            sections=[
                Section.Code(code=Op.PUSH1[190] + Op.PUSH1[0] + Op.RJUMPI[1] +
                    Op.POP + Op.PUSH1[0] + Op.RJUMPI[-11] +
                    Op.STOP,
                    max_stack_height=3),
            ],
            expected_bytecode="ef0001010004020001000e040000000080000360be6000e10001506000e1fff500",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),

    ],
    ids = lambda c: c.name,
)
def test_backwards_rjumpi(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test RJUMPI jumping backwards."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
