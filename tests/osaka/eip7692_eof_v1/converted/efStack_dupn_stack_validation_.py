import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='dupn_stack_validation_0',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e60000",
        ),
        Container(
            name='dupn_stack_validation_1',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e61300",
        ),
        Container(
            name='dupn_stack_validation_2',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e61400",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='dupn_stack_validation_3',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6d000",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='dupn_stack_validation_4',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6fe00",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='dupn_stack_validation_5',
            raw_bytes="ef0001010004020001002b040000000080001560016001600160016001600160016001600160016001600160016001600160016001600160016001e6ff00",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
