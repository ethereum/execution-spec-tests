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
            name='forwards_rjump_variable_stack_0',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.RJUMP[0] + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000035f6000e100025f5fe0000000",
        ),
        Container(
            name='forwards_rjump_variable_stack_1',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[3] + Op.RJUMP[1] + Op.NOT + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e10003e000011900",
        ),
        Container(
            name='forwards_rjump_variable_stack_2',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[8] + Op.PUSH1(0) + Op.RJUMPI[6] + Op.RJUMP[4] + Op.RJUMP[1] + Op.NOT + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000055f6000e100025f5f5f6000e100086000e10006e00004e000011900",
        ),
        Container(
            name='forwards_rjump_variable_stack_3',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[3] + Op.RJUMP[1] + Op.PUSH0 + Op.STOP,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e10003e000015f00",
        ),
        Container(
            name='forwards_rjump_variable_stack_4',
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[8] + Op.PUSH1(0) + Op.RJUMPI[7] + Op.RJUMP[5] + Op.PUSH0 + Op.RJUMP[1] + Op.NOT + Op.STOP,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000045f6000e100025f5f6000e100086000e10007e000055fe000011900",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
