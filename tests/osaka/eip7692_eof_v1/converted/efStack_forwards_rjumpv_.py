import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='forwards_rjumpv_0',
            raw_bytes="ef0001010004020001000704000000008000016001e200000000",
        ),
        Container(
            name='forwards_rjumpv_1',
            raw_bytes="ef0001010004020001000904000000008000025f6000e20000011900",
        ),
        Container(
            name='forwards_rjumpv_2',
            raw_bytes="ef0001010004020001000d04000000008000025f6000e201000200035f501900",
        ),
        Container(
            name='forwards_rjumpv_3',
            raw_bytes="ef0001010004020001000904000000008000025f6000e20000015f00",
        ),
        Container(
            name='forwards_rjumpv_4',
            raw_bytes="ef0001010004020001000d04000000008000035f6000e201000100025f5f1900",
        ),
        Container(
            name='forwards_rjumpv_5',
            raw_bytes="ef0001010004020001001604000000008000025f6000e2010005000a6001e000076002e00002600300",
        ),
        Container(
            name='forwards_rjumpv_6',
            raw_bytes="ef0001010004020001001604000000008000045f6000e201000400095fe000085f5fe000035f5f5f00",
        ),
        Container(
            name='forwards_rjumpv_7',
            raw_bytes="ef0001010004020001001904000000008000055f5f5f5f6000e2010004000950e000085050e0000350505000",
        ),
        Container(
            name='forwards_rjumpv_8',
            raw_bytes="ef0001010004020001000b04000000008000025f6000e2000003e0000000",
        ),
        Container(
            name='forwards_rjumpv_9',
            raw_bytes="ef0001010004020001000c04000000008000025f6000e20000045fe0000000",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
