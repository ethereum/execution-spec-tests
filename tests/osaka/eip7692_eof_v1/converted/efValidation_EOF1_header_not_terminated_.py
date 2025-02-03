import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_header_not_terminated_6',
            raw_bytes="ef00010100040200010001040001",
            validity_error=EOFException.MISSING_HEADERS_TERMINATOR,
        ),
        Container(
            name='EOF1_header_not_terminated_7',
            raw_bytes="ef00010100040200010001040001feaa",
            validity_error=EOFException.MISSING_TERMINATOR,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
