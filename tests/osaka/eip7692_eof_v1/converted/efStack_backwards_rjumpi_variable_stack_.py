import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='backwards_rjumpi_variable_stack_0',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[-5] + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffb00",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_1',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPI[-7] + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001004000000008000045f6000e100025f5f5f506000e1fff900",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_2',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPI[-7] + Op.PUSH1(0) + Op.RJUMPI[-12] + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001504000000008000045f6000e100025f5f5f506000e1fff96000e1fff400",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_3',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPI[-7] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[-13] + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001604000000008000055f6000e100025f5f5f506000e1fff95f6000e1fff300",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_4',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(1) + Op.ADD + Op.DUP1 + Op.RJUMPI[-7] + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001104000000008000055f6000e100025f5f5f60010180e1fff900",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_5',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(1) + Op.ADD + Op.DUP1 + Op.DUP1 + Op.RJUMPI[-8] + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001204000000008000055f6000e100025f5f5f6001018080e1fff800",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_6',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.RJUMPI[-4] + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001004000000008000055f6000e100025f5f5f5f5f50e1fffc00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_7',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPI[-7] + Op.RJUMP[-10],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001204000000008000045f6000e100025f5f5f506000e1fff9e0fff6",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_8',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPI[-7] + Op.PUSH0 + Op.RJUMP[-11],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001304000000008000045f6000e100025f5f5f506000e1fff95fe0fff5",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
