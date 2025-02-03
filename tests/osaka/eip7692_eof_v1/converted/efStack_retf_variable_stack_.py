import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='retf_variable_stack_0',
            raw_bytes="ef000101000802000200040009040000000080000500050003e30001005f6000e100025f5fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='retf_variable_stack_1',
            raw_bytes="ef000101000802000200040009040000000080000300030003e30001005f6000e100025f5fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='retf_variable_stack_2',
            raw_bytes="ef000101000802000200040009040000000080000100010003e30001005f6000e100025f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name='retf_variable_stack_3',
            raw_bytes="ef000101000802000200040009040000000080000000000003e30001005f6000e100025f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
