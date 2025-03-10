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
            name="underflow_0",
            sections=[
                Section.Code(
                    code=Op.ADD + Op.STOP,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001 010004 0200010002 04000000 00800001 0100",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_1",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef00010100080200020004000204000000 00800001 01020002 e30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_2",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=0,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000c020003000400030002 04000000 00800002 00020000 01020002 e3000100 e50002 5fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_3",
            sections=[
                Section.Code(
                    code=Op.JUMPF[1],
                ),
                Section.Code(
                    code=Op.PUSH1[0] + Op.PUSH1[0] + Op.REVERT,
                    code_inputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef00010100080200020003000504000000 00800000 01800003 e5000160006000fd",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
