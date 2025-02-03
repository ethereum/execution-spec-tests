import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='ymlExample_0',
            raw_bytes="60016000f3",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='ymlExample_1',
            raw_bytes="efffff",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='ymlExample_2',
            raw_bytes="610badfe",
            validity_error=EOFException.INVALID_MAGIC,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
