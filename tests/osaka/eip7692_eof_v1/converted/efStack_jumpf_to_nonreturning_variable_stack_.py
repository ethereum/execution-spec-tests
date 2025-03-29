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
            name="jumpf_to_nonreturning_variable_stack_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=5, max_stack_height=5),
            ],
            expected_bytes="ef0001010008020002000b00010400000000800003058000055f6000e100025f5fe50001fe",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=3, max_stack_height=3),
            ],
            expected_bytes="ef0001010008020002000b00010400000000800003038000035f6000e100025f5fe50001fe",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID, code_inputs=1, max_stack_height=1),
            ],
            expected_bytes="ef0001010008020002000b00010400000000800003018000015f6000e100025f5fe50001fe",
        ),
        Container(
            name="jumpf_to_nonreturning_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[1],
                    max_stack_height=3,
                ),
                Section.Code(code=Op.INVALID),
            ],
            expected_bytes="ef0001010008020002000b00010400000000800003008000005f6000e100025f5fe50001fe",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
