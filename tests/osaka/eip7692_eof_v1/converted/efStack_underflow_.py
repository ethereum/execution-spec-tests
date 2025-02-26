import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="underflow_0",
            raw_bytes="ef0001010004020001000204000000008000000100",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_1",
            raw_bytes="ef000101000802000200040002040000000080000101020002e30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_2",
            raw_bytes="ef000101000c02000300040003000204000000008000020002000001020002e3000100e500025fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_3",
            raw_bytes="ef000101000802000200030005040000000080000001800003e5000160006000fd",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
