import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='jumpf_to_nonreturning_variable_stack_0',
            raw_bytes="ef0001010008020002000b00010400000000800003058000055f6000e100025f5fe50001fe",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='jumpf_to_nonreturning_variable_stack_1',
            raw_bytes="ef0001010008020002000b00010400000000800003038000035f6000e100025f5fe50001fe",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='jumpf_to_nonreturning_variable_stack_2',
            raw_bytes="ef0001010008020002000b00010400000000800003018000015f6000e100025f5fe50001fe",
        ),
        Container(
            name='jumpf_to_nonreturning_variable_stack_3',
            raw_bytes="ef0001010008020002000b00010400000000800003008000005f6000e100025f5fe50001fe",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
