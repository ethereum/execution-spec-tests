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
            name="callf_stack_validation_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.CALLF[2] + Op.RETF,
                    code_outputs=1,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=2,
                    code_outputs=1,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040006000204000000008000010001000202010002e30001005f5fe30002e450e4",
        ),
        Container(
            name="callf_stack_validation_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.CALLF[2] + Op.RETF,
                    code_outputs=1,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=2,
                    code_outputs=1,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040007000204000000008000010001000302010002e30001005f5f5fe30002e450e4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name="callf_stack_validation_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[2] + Op.RETF,
                    code_outputs=1,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.POP + Op.RETF,
                    code_inputs=2,
                    code_outputs=1,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c02000300040005000204000000008000010001000102010002e30001005fe30002e450e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
