import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='jumpf_to_nonreturning_0',
            raw_bytes="ef000101000802000200030001040000000080000000800000e5000100",
        ),
        Container(
            name='jumpf_to_nonreturning_1',
            raw_bytes="ef0001010008020002000500010400000000800002008000005f5fe5000100",
        ),
        Container(
            name='jumpf_to_nonreturning_2',
            raw_bytes="ef0001010008020002000600010400000000800003038000035f5f5fe5000100",
        ),
        Container(
            name='jumpf_to_nonreturning_3',
            raw_bytes="ef0001010008020002000700010400000000800004038000035f5f5f5fe5000100",
        ),
        Container(
            name='jumpf_to_nonreturning_4',
            raw_bytes="ef0001010008020002000500010400000000800002038000035f5fe5000100",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
