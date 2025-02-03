import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='forwards_rjump_0',
            raw_bytes="ef000101000402000100040400000000800000e0000000",
        ),
        Container(
            name='forwards_rjump_1',
            raw_bytes="ef0001010004020001000b04000000008000025f6000e10003e000011900",
        ),
        Container(
            name='forwards_rjump_2',
            raw_bytes="ef0001010004020001001304000000008000025f6000e100086000e10006e00004e000011900",
        ),
        Container(
            name='forwards_rjump_3',
            raw_bytes="ef0001010004020001000b04000000008000025f6000e10003e000015f00",
        ),
        Container(
            name='forwards_rjump_4',
            raw_bytes="ef0001010004020001001404000000008000025f6000e100086000e10007e000055fe000011900",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
