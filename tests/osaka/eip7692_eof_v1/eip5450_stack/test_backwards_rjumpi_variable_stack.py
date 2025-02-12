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
            name="backwards_rjumpi_variable_stack_0",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    2 + Op.PUSH1[0] + Op.RJUMPI[-5] + Op.STOP,
                    max_stack_height=4),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffb00",
          ),
        Container(
            name="backwards_rjumpi_variable_stack_1",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] +
                    Op.STOP,
                    max_stack_height=4),
            ],
            expected_bytecode="ef0001010004020001001004000000008000045f6000e100025f5f5f506000e1fff900",
          ),
        Container(
            name="backwards_rjumpi_variable_stack_2",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] +
                    Op.PUSH1[0] + Op.RJUMPI[-12] + Op.STOP,
                    max_stack_height=4),
            ],
            expected_bytecode="ef0001010004020001001504000000008000045f6000e100025f5f5f506000e1fff96000e1fff400",
          ),
        Container(
            name="backwards_rjumpi_variable_stack_3",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] +
                    Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[-13] +
                    Op.STOP,
                    max_stack_height=5),
            ],
            expected_bytecode="ef0001010004020001001604000000008000055f6000e100025f5f5f506000e1fff95f6000e1fff300",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_variable_stack_4",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.PUSH1[1] + Op.ADD + Op.DUP1 +
                    Op.RJUMPI[-7] + Op.STOP,
                    max_stack_height=5),
            ],
            expected_bytecode="ef0001010004020001001104000000008000055f6000e100025f5f5f60010180e1fff900",
          ),
        Container(
            name="backwards_rjumpi_variable_stack_5",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.PUSH1[1] + Op.ADD + Op.DUP1 * 2 +
                    Op.RJUMPI[-8] + Op.STOP,
                    max_stack_height=5),
            ],
            expected_bytecode="ef0001010004020001001204000000008000055f6000e100025f5f5f6001018080e1fff800",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_variable_stack_6",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    5 + Op.POP + Op.RJUMPI[-4] + Op.STOP,
                    max_stack_height=5),
            ],
            expected_bytecode="ef0001010004020001001004000000008000055f6000e100025f5f5f5f5f50e1fffc00",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),
        Container(
            name="backwards_rjumpi_variable_stack_7",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] +
                    Op.RJUMP[-10],
                    max_stack_height=4),
            ],
            expected_bytecode="ef0001010004020001001204000000008000045f6000e100025f5f5f506000e1fff9e0fff6",
          ),
        Container(
            name="backwards_rjumpi_variable_stack_8",
            sections=[
                Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 *
                    3 + Op.POP + Op.PUSH1[0] + Op.RJUMPI[-7] +
                    Op.PUSH0 + Op.RJUMP[-11],
                    max_stack_height=4),
            ],
            expected_bytecode="ef0001010004020001001304000000008000045f6000e100025f5f5f506000e1fff95fe0fff5",
            validity_error=[
                EOFException.STACK_HEIGHT_MISMATCH
            ],
          ),

    ],
    ids = lambda c: c.name,
)
def test_backwards_rjumpi_variable_stack(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test RJUMPI jumping backwards with variable stack."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
