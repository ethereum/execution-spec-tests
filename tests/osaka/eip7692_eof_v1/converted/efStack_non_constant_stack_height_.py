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
            name="non_constant_stack_height_0",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=4,
                ),
            ],
        ),
        Container(
            name="non_constant_stack_height_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 2
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=5,
                ),
            ],
        ),
        Container(
            name="non_constant_stack_height_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.RJUMPI[7]
                    + Op.PUSH0 * 3
                    + Op.RJUMPI[1]
                    + Op.POP * 2
                    + Op.PUSH0 * 2
                    + Op.REVERT,
                    max_stack_height=4,
                ),
            ],
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
