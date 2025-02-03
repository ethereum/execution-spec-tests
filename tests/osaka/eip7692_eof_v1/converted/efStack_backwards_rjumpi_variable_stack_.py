import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='backwards_rjumpi_variable_stack_0',
            raw_bytes="ef0001010004020001000e04000000008000045f6000e100025f5f6000e1fffb00",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_1',
            raw_bytes="ef0001010004020001001004000000008000045f6000e100025f5f5f506000e1fff900",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_2',
            raw_bytes="ef0001010004020001001504000000008000045f6000e100025f5f5f506000e1fff96000e1fff400",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_3',
            raw_bytes="ef0001010004020001001604000000008000055f6000e100025f5f5f506000e1fff95f6000e1fff300",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_4',
            raw_bytes="ef0001010004020001001104000000008000055f6000e100025f5f5f60010180e1fff900",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_5',
            raw_bytes="ef0001010004020001001204000000008000055f6000e100025f5f5f6001018080e1fff800",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_6',
            raw_bytes="ef0001010004020001001004000000008000055f6000e100025f5f5f5f5f50e1fffc00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_variable_stack_7',
            raw_bytes="ef0001010004020001001204000000008000045f6000e100025f5f5f506000e1fff9e0fff6",
        ),
        Container(
            name='backwards_rjumpi_variable_stack_8',
            raw_bytes="ef0001010004020001001304000000008000045f6000e100025f5f5f506000e1fff95fe0fff5",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
