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
            name="jumpf_to_returning_variable_stack_0",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=5,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000204000000008000030003000305030003e30001005f6000e100025f5fe500025fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_1",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.RETF,
                    code_inputs=3,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000104000000008000030003000303030003e30001005f6000e100025f5fe50002e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_2",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 * 2 + Op.RETF,
                    code_inputs=1,
                    code_outputs=3,
                    max_stack_height=5,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000304000000008000030003000301030005e30001005f6000e100025f5fe500025f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_3",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=3,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.RETF,
                    code_outputs=3,
                    max_stack_height=3,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000404000000008000030003000300030003e30001005f6000e100025f5fe500025f5f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_4",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP * 4 + Op.RETF,
                    code_inputs=5,
                    code_outputs=1,
                    max_stack_height=5,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000504000000008000020002000305010005e30001005f6000e100025f5fe5000250505050e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_5",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.POP * 2 + Op.RETF,
                    code_inputs=3,
                    code_outputs=1,
                    max_stack_height=3,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000304000000008000020002000303010003e30001005f6000e100025f5fe500025050e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_6",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.RETF,
                    code_inputs=1,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000104000000008000020002000301010001e30001005f6000e100025f5fe50002e4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name="jumpf_to_returning_variable_stack_7",
            sections=[
                Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.JUMPF[2],
                    code_outputs=2,
                    max_stack_height=3,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_outputs=1,
                    max_stack_height=1,
                ),
            ],
            expected_bytes="ef000101000c0200030004000b000204000000008000020002000300010001e30001005f6000e100025f5fe500025fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
