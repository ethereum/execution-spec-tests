import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_invalid_section_0_type_1',
            raw_bytes="ef00010100040200010003040000000001000060005c",
            validity_error=EOFException.INVALID_FIRST_SECTION_TYPE,
        ),
        Container(
            name='EOF1_invalid_section_0_type_2',
            raw_bytes="ef000101000402000100010400000001800000fe",
            validity_error=EOFException.INVALID_FIRST_SECTION_TYPE,
        ),
        Container(
            name='EOF1_invalid_section_0_type_3',
            raw_bytes="ef00010100040200010003040000000203000060005c",
            validity_error=EOFException.INVALID_FIRST_SECTION_TYPE,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
