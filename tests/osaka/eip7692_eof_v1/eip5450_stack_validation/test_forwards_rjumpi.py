""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-5450.md"
REFERENCE_SPEC_VERSION = "9c7c91bf7b9b7af9e76248f7921a03ddc17f99ef"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.RJUMPI[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000016001e1000000",
              None,
              id="forwards_rjumpi_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000025f6000e100011900",
              None,
              id="forwards_rjumpi_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[6] + Op.PUSH1[0] + Op.RJUMPI[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000025f6000e100066000e100011900",
              None,
              id="forwards_rjumpi_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000025f6000e100015f00",
              None,
              id="forwards_rjumpi_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[7] + Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.NOT + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000035f6000e100075f6000e100011900",
              None,
              id="forwards_rjumpi_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[1] + Op.ADD + Op.DUP1 + Op.PUSH1[10] + Op.GT + Op.RJUMPI[4] + Op.DUP1 + Op.RJUMPI[-14] + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000035f60010180600a11e1000480e1fff200",
              None,
              id="forwards_rjumpi_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[1] + Op.ADD + Op.DUP1 + Op.PUSH1[10] + Op.GT + Op.RJUMPI[5] + Op.PUSH0 + Op.DUP1 + Op.RJUMPI[-13] + Op.STOP, max_stack_height=3),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000035f60010180600a11e100055f80e1fff300",
              None,
              id="forwards_rjumpi_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[1] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000025f6000e100045fe000015f00",
              None,
              id="forwards_rjumpi_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000025f6000e100045fe000011900",
              None,
              id="forwards_rjumpi_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[4] + Op.POP + Op.RJUMP[1] + Op.POP + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000025f6000e1000450e000015000",
              None,
              id="forwards_rjumpi_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[4] + Op.POP + Op.RJUMP[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000025f6000e1000450e000011900",
              None,
              id="forwards_rjumpi_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[3] + Op.RJUMP[0] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000025f6000e10003e0000000",
              None,
              id="forwards_rjumpi_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[0] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000025f6000e100045fe0000000",
              None,
              id="forwards_rjumpi_12"
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
