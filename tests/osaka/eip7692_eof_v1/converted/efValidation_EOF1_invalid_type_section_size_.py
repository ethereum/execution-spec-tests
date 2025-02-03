import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_invalid_type_section_size_0',
            raw_bytes="ef000101000102000100010400000000fe",
            validity_error=EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        Container(
            name='EOF1_invalid_type_section_size_1',
            raw_bytes="ef00010100020200010001040000000080fe",
            validity_error=EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        Container(
            name='EOF1_invalid_type_section_size_2',
            raw_bytes="ef00010100080200010001040000000080000000000000fe",
            validity_error=EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
        Container(
            name='EOF1_invalid_type_section_size_4',
            raw_bytes="ef00010100100200030001000100010400000000800000008000000080000000800000fefefe",
            validity_error=EOFException.INVALID_TYPE_SECTION_SIZE,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
