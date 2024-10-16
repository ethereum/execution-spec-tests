""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7480.md"
REFERENCE_SPEC_VERSION = "d1cafe61fa83c0f2a752bb0aaf220cd0d20bca98"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.DATALOADN[0] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333")
                ],
              )
              ,
              "ef000101000402000100050400200000800001d1000050000000000000000000111111111111111122222222222222223333333333333333",
              None,
              id="dataloadn_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.DATALOADN[1] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="000000000000000011111111111111112222222222222222333333333333333344")
                ],
              )
              ,
              "ef000101000402000100050400210000800001d100015000000000000000000011111111111111112222222222222222333333333333333344",
              None,
              id="dataloadn_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.DATALOADN[32] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="00000000000000001111111111111111222222222222222233333333333333330000000000000000111111111111111122222222222222223333333333333333")
                ],
              )
              ,
              "ef000101000402000100050400400000800001d10020500000000000000000001111111111111111222222222222222233333333333333330000000000000000111111111111111122222222222222223333333333333333",
              None,
              id="dataloadn_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.DATALOADN[0] + Op.POP + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100050400000000800001d100005000",
              EOFException.INVALID_DATALOADN_INDEX,
              id="dataloadn_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.DATALOADN[1] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="00")
                ],
              )
              ,
              "ef000101000402000100050400010000800001d10001500000",
              EOFException.INVALID_DATALOADN_INDEX,
              id="dataloadn_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.DATALOADN[32] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333")
                ],
              )
              ,
              "ef000101000402000100050400200000800001d1002050000000000000000000111111111111111122222222222222223333333333333333",
              EOFException.INVALID_DATALOADN_INDEX,
              id="dataloadn_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.DATALOADN[-1] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="0000000000000000111111111111111122222222222222223333333333333333")
                ],
              )
              ,
              "ef000101000402000100050400200000800001d1ffff50000000000000000000111111111111111122222222222222223333333333333333",
              EOFException.INVALID_DATALOADN_INDEX,
              id="dataloadn_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.DATALOADN[32] + Op.POP + Op.STOP, max_stack_height=1),
                    Section.Data(data="000000000000000011111111111111112222222222222222333333333333333300000000000000001111111111111111222222222222222233333333333333")
                ],
              )
              ,
              "ef0001010004020001000504003f0000800001d100205000000000000000000011111111111111112222222222222222333333333333333300000000000000001111111111111111222222222222222233333333333333",
              EOFException.INVALID_DATALOADN_INDEX,
              id="dataloadn_7"
        ),
        
    ]
)

def test_example_valid_invalid(
    eof_test: EOFTestFiller,
    eof_code: Container,
    expected_hex_bytecode: str,
    exception: EOFException | None,
):
    """
    Verify eof container construction and exception
    """
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
