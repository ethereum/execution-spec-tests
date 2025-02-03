import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
    'container',
    [
        Container(
            name='EOF1_eofcreate_invalid_0',
            raw_bytes="ef0001010004020001000903000100140400000000800004600060ff60006000ecef000101000402000100010400000000800000fe",
            validity_error=EOFException.TRUNCATED_INSTRUCTION,
        ),
        Container(
            name='EOF1_eofcreate_invalid_1',
            raw_bytes="ef0001010004020001000a03000100140400000000800004600060ff60006000ec00ef000101000402000100010400000000800000fe",
            validity_error=EOFException.MISSING_STOP_OPCODE,
        ),
        Container(
            name='EOF1_eofcreate_invalid_2',
            raw_bytes="ef0001010004020001000c03000100140400000000800004600060ff60006000ec015000ef000101000402000100010400000000800000fe",
            validity_error=EOFException.INVALID_CONTAINER_SECTION_INDEX,
        ),
        Container(
            name='EOF1_eofcreate_invalid_3',
            raw_bytes="ef0001010004020001000c03000100140400000000800004600060ff60006000ecff5000ef000101000402000100010400000000800000fe",
            validity_error=EOFException.INVALID_CONTAINER_SECTION_INDEX,
        ),
        Container(
            name='EOF1_eofcreate_invalid_4',
            raw_bytes="ef0001010004020001000c03000100160400000000800004600060ff60006000ec005000ef000101000402000100010400030000800000feaabb",
            validity_error=EOFException.EOFCREATE_WITH_TRUNCATED_CONTAINER,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
