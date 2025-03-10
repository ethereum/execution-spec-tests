import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="underflow_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.LOG2 + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000035f6000e100025f5fa200",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.ADD + Op.STOP,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000035f6000e100025f5f0100",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=4,
                    code_outputs=5,
                    max_stack_height=5,
                ),
            ],
            expected_bytecode="ef0001010008020002000c000204000000 00800004 04050005 5f6000e100025f5fe30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=3,
                    code_outputs=4,
                    max_stack_height=4,
                ),
            ],
            expected_bytecode="ef0001010008020002000c000204000000 00800004 03040004 5f6000e100025f5fe30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_4",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP + Op.POP + Op.RETF,
                    code_inputs=5,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef0001 01000c 0200030004000b0003 04000000 00800003 00030003 05030003 e30001 00 5f6000e100025f5fe50002 5050e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_6",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(
                    code= Op.PUSH1[0] + Op.PUSH1[0] + Op.REVERT,
                    code_inputs=4,
                    max_stack_height=6,
                ),
            ],
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_7",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(
                    code= Op.PUSH1[0] + Op.PUSH1[0] + Op.REVERT,
                    code_inputs=3,
                    max_stack_height=5,
                ),
            ],
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
