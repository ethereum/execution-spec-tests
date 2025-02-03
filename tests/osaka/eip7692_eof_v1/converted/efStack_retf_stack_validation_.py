import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='retf_stack_validation_0',
            raw_bytes="ef000101000802000200040003040000000080000200020002e30001005f5fe4",
        ),
        Container(
            name='retf_stack_validation_1',
            raw_bytes="ef000101000802000200040002040000000080000200020001e30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='retf_stack_validation_2',
            raw_bytes="ef000101000802000200040004040000000080000200020003e30001005f5f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name='retf_stack_validation_3',
            raw_bytes="ef00010100080200020005000d0400000000800002010200025fe3000100e1000760016001e000025f5fe4",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
