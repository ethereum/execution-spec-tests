import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='jumpf_to_returning_0',
            raw_bytes="ef000101000c02000300040003000304000000008000020002000000020002e3000100e500025f5fe4",
        ),
        Container(
            name='jumpf_to_returning_1',
            raw_bytes="ef000101000c02000300040005000304000000008000020002000200020002e30001005f5fe500025f5fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name='jumpf_to_returning_10',
            raw_bytes="ef000101000c02000300040006000304000000008000020002000303010003e30001005f5f5fe500025050e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='jumpf_to_returning_2',
            raw_bytes="ef000101000c02000300040006000204000000008000020002000303020003e30001005f5f5fe5000250e4",
        ),
        Container(
            name='jumpf_to_returning_3',
            raw_bytes="ef000101000c02000300040007000204000000008000020002000403020003e30001005f5f5f5fe5000250e4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name='jumpf_to_returning_4',
            raw_bytes="ef000101000c02000300040005000204000000008000020002000203020003e30001005f5fe5000250e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='jumpf_to_returning_5',
            raw_bytes="ef000101000c02000300040004000204000000008000020002000100010001e30001005fe500025fe4",
        ),
        Container(
            name='jumpf_to_returning_6',
            raw_bytes="ef000101000c02000300040006000204000000008000020002000300010001e30001005f5f5fe500025fe4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
        Container(
            name='jumpf_to_returning_7',
            raw_bytes="ef000101000c02000300040003000204000000008000020002000000010001e3000100e500025fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name='jumpf_to_returning_8',
            raw_bytes="ef000101000c02000300040007000304000000008000020002000403010003e30001005f5f5f5fe500025050e4",
        ),
        Container(
            name='jumpf_to_returning_9',
            raw_bytes="ef000101000c02000300040008000304000000008000020002000503010003e30001005f5f5f5f5fe500025050e4",
            validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
