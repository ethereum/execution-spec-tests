import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


rjumpis_1023 = Op.STOP()
offset = 1
for _ in range(0, 1023):
    rjumpis_1023 = Op.PUSH0 + Op.RJUMPI[offset] + Op.PUSH0 + rjumpis_1023
    offset += 5

rjumpis_1024 = Op.PUSH0 + Op.RJUMPI[offset] + Op.PUSH0 + rjumpis_1023

@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="invalid_1024_rjumpis",
            sections=[
                Section.Code(code=rjumpis_1024, max_stack_height=1023),
            ],
            validity_error=EOFException.INVALID_MAX_STACK_INCREASE,
        ),
        Container(
            name="valid_1023_rjumpis",
            sections=[
                Section.Code(code=rjumpis_1023, max_stack_height=1023),
            ],
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
