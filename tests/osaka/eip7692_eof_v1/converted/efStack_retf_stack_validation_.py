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
            name="retf_stack_validation_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef000101000802000200040003040000000080000200020002e30001005f5fe4",
        ),
        Container(
            name="retf_stack_validation_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef000101000802000200040002040000000080000200020001e30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="retf_stack_validation_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.RETF,
                    code_outputs=2,
                    max_stack_height=3,
                ),
            ],
            expected_bytecode="ef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name="retf_stack_validation_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.RJUMPI[7] + Op.PUSH1[1] * 2 + Op.RJUMP[2] + Op.PUSH0 * 2 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
            expected_bytecode="ef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
