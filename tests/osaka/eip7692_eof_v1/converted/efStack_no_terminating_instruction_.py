import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='no_terminating_instruction_0',
            raw_bytes="ef0001010004020001000104000000008000005f",
            validity_error=EOFException.MISSING_STOP_OPCODE,
        ),
        Container(
            name='no_terminating_instruction_1',
            raw_bytes="ef0001010004020001000504000000008000006002600101",
            validity_error=EOFException.MISSING_STOP_OPCODE,
        ),
        Container(
            name='no_terminating_instruction_2',
            raw_bytes="ef0001010004020001000504000000008000006001e1fffb",
            validity_error=EOFException.MISSING_STOP_OPCODE,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
