import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='forwards_rjumpi_0',
            raw_bytes="ef0001010004020001000604000000008000016001e1000000",
        ),
        Container(
            name='forwards_rjumpi_1',
            raw_bytes="ef0001010004020001000804000000008000025f6000e100011900",
        ),
        Container(
            name='forwards_rjumpi_10',
            raw_bytes="ef0001010004020001000c04000000008000025f6000e1000450e000011900",
        ),
        Container(
            name='forwards_rjumpi_11',
            raw_bytes="ef0001010004020001000a04000000008000025f6000e10003e0000000",
        ),
        Container(
            name='forwards_rjumpi_12',
            raw_bytes="ef0001010004020001000b04000000008000025f6000e100045fe0000000",
        ),
        Container(
            name='forwards_rjumpi_2',
            raw_bytes="ef0001010004020001000d04000000008000025f6000e100066000e100011900",
        ),
        Container(
            name='forwards_rjumpi_3',
            raw_bytes="ef0001010004020001000804000000008000025f6000e100015f00",
        ),
        Container(
            name='forwards_rjumpi_4',
            raw_bytes="ef0001010004020001000e04000000008000035f6000e100075f6000e100011900",
        ),
        Container(
            name='forwards_rjumpi_5',
            raw_bytes="ef0001010004020001001004000000008000035f60010180600a11e1000480e1fff200",
        ),
        Container(
            name='forwards_rjumpi_6',
            raw_bytes="ef0001010004020001001104000000008000035f60010180600a11e100055f80e1fff300",
        ),
        Container(
            name='forwards_rjumpi_7',
            raw_bytes="ef0001010004020001000c04000000008000025f6000e100045fe000015f00",
        ),
        Container(
            name='forwards_rjumpi_8',
            raw_bytes="ef0001010004020001000c04000000008000025f6000e100045fe000011900",
        ),
        Container(
            name='forwards_rjumpi_9',
            raw_bytes="ef0001010004020001000c04000000008000025f6000e1000450e000015000",
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
