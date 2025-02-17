import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='forwards_rjumpv_variable_stack_0',
            raw_bytes="ef0001010004020001000f04000000008000045f6000e100025f5f6001e200000000",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_1',
            raw_bytes="ef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000011900",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_2',
            raw_bytes="ef0001010004020001001504000000008000055f6000e100025f5f5f6000e201000200035f501900",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_3',
            raw_bytes="ef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000015f00",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_4',
            raw_bytes="ef0001010004020001001504000000008000065f6000e100025f5f5f6000e201000100025f5f1900",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_5',
            raw_bytes="ef0001010004020001001e04000000008000055f6000e100025f5f5f6000e2010005000a6001e000076002e00002600300",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_6',
            raw_bytes="ef0001010004020001001e04000000008000075f6000e100025f5f5f6000e201000400095fe000085f5fe000035f5f5f00",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_7',
            raw_bytes="ef0001010004020001002104000000008000085f6000e100025f5f5f5f5f5f6000e2010004000950e000085050e0000350505000",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_8',
            raw_bytes="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e2000003e0000000",
        ),
        Container(
            name='forwards_rjumpv_variable_stack_9',
            raw_bytes="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e20000045fe0000000",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
