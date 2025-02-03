import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_multiple_type_sections_0',
            raw_bytes="ef000101000401000402000200010001000080000000800000fefe",
            validity_error=EOFException.MISSING_CODE_HEADER,
        ),
        Container(
            name='EOF1_multiple_type_sections_1',
            raw_bytes="ef0001030002010001010001040002000000fefe0000",
            validity_error=EOFException.MISSING_TYPE_HEADER,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
