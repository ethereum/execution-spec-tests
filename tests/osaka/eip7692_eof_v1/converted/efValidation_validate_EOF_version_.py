import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='valid_except_version_00',
            raw_bytes="ef000001000402000100030200040000800000600000aabbccdd",
            validity_error=EOFException.INVALID_VERSION,
        ),
        Container(
            name='valid_except_version_02',
            raw_bytes="ef000201000402000100030200040000800000600000aabbccdd",
            validity_error=EOFException.INVALID_VERSION,
        ),
        Container(
            name='valid_except_version_FF',
            raw_bytes="ef00ff01000402000100030200040000800000600000aabbccdd",
            validity_error=EOFException.INVALID_VERSION,
        ),
        Container(
            name='validate_EOF_version_0',
            raw_bytes="ef0002",
            validity_error=EOFException.INVALID_VERSION,
        ),
        Container(
            name='validate_EOF_version_1',
            raw_bytes="ef00ff",
            validity_error=EOFException.INVALID_VERSION,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
