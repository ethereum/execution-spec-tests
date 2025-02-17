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
            name='backwards_rjump_variable_stack_0',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.RJUMP[-3],
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000035f6000e100025f5fe0fffd",
        ),
        Container(
            name='backwards_rjump_variable_stack_1',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.RJUMP[-5],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000045f6000e100025f5f5f50e0fffb",
        ),
        Container(
            name='backwards_rjump_variable_stack_2',
            sections=[
                Section.Code(
                    code=(
                        Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP +
                        Op.PUSH1(1) + Op.RJUMPI[3] + Op.RJUMP[-8] + Op.RJUMP[-11]
                    ),
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001504000000008000045f6000e100025f5f5f506001e10003e0fff8e0fff5",
        ),
        Container(
            name='backwards_rjump_variable_stack_3',
            sections=[
                Section.Code(
                    code=(
                        Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP +
                        Op.PUSH1(1) + Op.RJUMPI[3] + Op.RJUMP[-8] + Op.PUSH0 + Op.RJUMP[-12]
                    ),
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001604000000008000045f6000e100025f5f5f506001e10003e0fff85fe0fff4",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_4',
            sections=[
                Section.Code(
                    code=(
                        Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) +
                        Op.RJUMPI[1] + Op.PUSH0 + Op.RJUMP[-7]
                    ),
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001104000000008000045f6000e100025f5f6000e100015fe0fff9",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_5',
            sections=[
                Section.Code(
                    code=(
                        Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) +
                        Op.RJUMPI[1] + Op.POP + Op.RJUMP[-7]
                    ),
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001104000000008000045f6000e100025f5f6000e1000150e0fff9",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_6',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.RJUMP[-4],
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000045f6000e100025f5f5fe0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_7',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.RJUMP[-4],
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000035f6000e100025f5f5f50e0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
