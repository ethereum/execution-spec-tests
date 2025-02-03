import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='rjumpi',
            raw_bytes="ef0001010004020001000604000000008000006000e1fffd00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='rjumpv',
            raw_bytes="ef0001010004020001000704000000008000006000e200fffc00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
