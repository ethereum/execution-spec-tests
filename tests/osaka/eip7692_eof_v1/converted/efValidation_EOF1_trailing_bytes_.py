import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_trailing_bytes_0',
            raw_bytes="ef000101000402000100010400000000800000fedeadbeef",
            validity_error=EOFException.INVALID_SECTION_BODIES_SIZE,
        ),
        Container(
            name='EOF1_trailing_bytes_1',
            raw_bytes="ef000101000402000100010400020000800000feaabbdeadbeef",
            validity_error=EOFException.INVALID_SECTION_BODIES_SIZE,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
