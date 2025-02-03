import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='valid_except_magic',
            raw_bytes="efff0101000402000100030300040000800000600000aabbccdd",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='validate_EOF_prefix_0',
            raw_bytes="00",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='validate_EOF_prefix_1',
            raw_bytes="fe",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='validate_EOF_prefix_3',
            raw_bytes="ef0101",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='validate_EOF_prefix_4',
            raw_bytes="efef01",
            validity_error=EOFException.INVALID_MAGIC,
        ),
        Container(
            name='validate_EOF_prefix_5',
            raw_bytes="efff01",
            validity_error=EOFException.INVALID_MAGIC,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
