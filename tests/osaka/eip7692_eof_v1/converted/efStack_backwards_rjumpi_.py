import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='backwards_rjumpi_0',
            raw_bytes="ef0001010004020001000604000000008000016000e1fffb00",
        ),
        Container(
            name='backwards_rjumpi_1',
            raw_bytes="ef0001010004020001000804000000008000015f506000e1fff900",
        ),
        Container(
            name='backwards_rjumpi_10',
            raw_bytes="ef0001010004020001000e040000000080000360be6000e10001506000e1fff500",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_2',
            raw_bytes="ef0001010004020001000d04000000008000015f506000e1fff96000e1fff400",
        ),
        Container(
            name='backwards_rjumpi_3',
            raw_bytes="ef0001010004020001000e04000000008000025f506000e1fff95f6000e1fff300",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_4',
            raw_bytes="ef0001010004020001000904000000008000025f60010180e1fff900",
        ),
        Container(
            name='backwards_rjumpi_5',
            raw_bytes="ef0001010004020001000a04000000008000025f6001018080e1fff800",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_6',
            raw_bytes="ef0001010004020001000804000000008000025f5f5f50e1fffc00",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_7',
            raw_bytes="ef0001010004020001000a04000000008000015f506000e1fff9e0fff6",
        ),
        Container(
            name='backwards_rjumpi_8',
            raw_bytes="ef0001010004020001000b04000000008000015f506000e1fff95fe0fff5",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name='backwards_rjumpi_9',
            raw_bytes="ef0001010004020001000d04000000008000035f6000e100015f6000e1fff500",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
