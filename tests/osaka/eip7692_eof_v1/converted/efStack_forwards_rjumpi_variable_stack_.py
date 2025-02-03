import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='forwards_rjumpi_variable_stack_0',
            raw_bytes="ef0001010004020001000e04000000008000045f6000e100025f5f6001e1000000",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_1',
            raw_bytes="ef0001010004020001001004000000008000055f6000e100025f5f5f6000e100011900",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_10',
            raw_bytes="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e1000450e000011900",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_11',
            raw_bytes="ef0001010004020001001204000000008000055f6000e100025f5f5f6000e10003e0000000",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_12',
            raw_bytes="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e100045fe0000000",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_2',
            raw_bytes="ef0001010004020001001504000000008000055f6000e100025f5f5f6000e100066000e100011900",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_3',
            raw_bytes="ef0001010004020001001004000000008000055f6000e100025f5f5f6000e100015f00",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_4',
            raw_bytes="ef0001010004020001001604000000008000065f6000e100025f5f5f6000e100075f6000e100011900",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_5',
            raw_bytes="ef0001010004020001001804000000008000065f6000e100025f5f5f60010180600a11e1000480e1fff200",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_6',
            raw_bytes="ef0001010004020001001904000000008000065f6000e100025f5f5f60010180600a11e100055f80e1fff300",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_7',
            raw_bytes="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e100045fe000015f00",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_8',
            raw_bytes="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e100045fe000011900",
        ),
        Container(
            name='forwards_rjumpi_variable_stack_9',
            raw_bytes="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e1000450e000015000",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
