import pytest

from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="underflow_variable_stack_0",
            raw_bytes="ef0001010004020001000a04000000008000035f6000e100025f5fa200",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_1",
            raw_bytes="ef0001010004020001000a04000000008000035f6000e100025f5f0100",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_2",
            raw_bytes="ef0001010008020002000c00020400000000800004040500055f6000e100025f5fe30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_3",
            raw_bytes="ef0001010008020002000c00020400000000800004030400045f6000e100025f5fe30001005fe4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_4",
            raw_bytes="ef000101000c0200030004000b000304000000008000030003000305030003e30001005f6000e100025f5fe500025050e4",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_6",
            raw_bytes="ef0001010008020002000b00050400000000800000058000075f6000e100025f5fe5000160006000fd",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
        Container(
            name="underflow_variable_stack_7",
            raw_bytes="ef0001010008020002000b00050400000000800000038000055f6000e100025f5fe5000160006000fd",
            validity_error=EOFException.STACK_UNDERFLOW,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
