import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='backwards_rjump_variable_stack_0',
            raw_bytes="ef0001010004020001000b04000000008000035f6000e100025f5fe0fffd",
        ),
        Container(
            name='backwards_rjump_variable_stack_1',
            raw_bytes="ef0001010004020001000d04000000008000045f6000e100025f5f5f50e0fffb",
        ),
        Container(
            name='backwards_rjump_variable_stack_2',
            raw_bytes="ef0001010004020001001504000000008000045f6000e100025f5f5f506001e10003e0fff8e0fff5",
        ),
        Container(
            name='backwards_rjump_variable_stack_3',
            raw_bytes="ef0001010004020001001604000000008000045f6000e100025f5f5f506001e10003e0fff85fe0fff4",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_4',
            raw_bytes="ef0001010004020001001104000000008000045f6000e100025f5f6000e100015fe0fff9",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_5',
            raw_bytes="ef0001010004020001001104000000008000045f6000e100025f5f6000e1000150e0fff9",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_6',
            raw_bytes="ef0001010004020001000c04000000008000045f6000e100025f5f5fe0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjump_variable_stack_7',
            raw_bytes="ef0001010004020001000d04000000008000035f6000e100025f5f5f50e0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
