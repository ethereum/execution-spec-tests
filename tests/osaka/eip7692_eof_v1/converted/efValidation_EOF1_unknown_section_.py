import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_unknown_section_0',
            raw_bytes="ef000105000100fe",
            validity_error=EOFException.MISSING_TYPE_HEADER,
        ),
        Container(
            name='EOF1_unknown_section_1',
            raw_bytes="ef0001ff000100fe",
            validity_error=EOFException.MISSING_TYPE_HEADER,
        ),
        Container(
            name='EOF1_unknown_section_2',
            raw_bytes="ef000101000402000100010500010000800000fe00",
            validity_error=EOFException.MISSING_DATA_SECTION,
        ),
        Container(
            name='EOF1_unknown_section_3',
            raw_bytes="ef00010100040200010001ff00010000800000fe00",
            validity_error=EOFException.MISSING_DATA_SECTION,
        ),
        Container(
            name='EOF1_unknown_section_4',
            raw_bytes="ef000101000402000100010400010500010000800000feaa00",
            validity_error=EOFException.MISSING_TERMINATOR,
        ),
        Container(
            name='EOF1_unknown_section_5',
            raw_bytes="ef00010100040200010001040001ff00010000800000feaa00",
            validity_error=EOFException.MISSING_TERMINATOR,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
