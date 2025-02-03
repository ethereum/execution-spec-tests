import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='non_constant_stack_height_0',
            raw_bytes="ef0001010004020001000e04000000008000045fe100075f5f5fe10001505f5ffd",
        ),
        Container(
            name='non_constant_stack_height_1',
            raw_bytes="ef0001010004020001000f04000000008000055f5fe100075f5f5fe10001505f5ffd",
        ),
        Container(
            name='non_constant_stack_height_2',
            raw_bytes="ef0001010004020001000f04000000008000045fe100075f5f5fe1000150505f5ffd",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
