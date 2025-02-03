import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_types_section_0_size_0',
            raw_bytes="ef0001010000020001000100fe",
            validity_error=EOFException.ZERO_SECTION_SIZE,
        ),
        Container(
            name='EOF1_types_section_0_size_1',
            raw_bytes="ef0001010000020001000104000100feda",
            validity_error=EOFException.ZERO_SECTION_SIZE,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
