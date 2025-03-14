import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="rjumpi",
            raw_bytes="ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffd00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name="rjumpv",
            raw_bytes="ef0001010004020001000f04000000008000045f6000e100025f5f6000e200fffc00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
