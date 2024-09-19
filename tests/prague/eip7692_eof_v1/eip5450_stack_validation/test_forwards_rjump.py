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
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[3] + Op.RJUMP[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000025f6000e10003e000011900",
              None,
              id="forwards_rjump_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[8] + Op.PUSH1[0] + Op.RJUMPI[6] + Op.RJUMP[4] + Op.RJUMP[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000025f6000e100086000e10006e00004e000011900",
              None,
              id="forwards_rjump_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[3] + Op.RJUMP[1] + Op.PUSH0 + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000025f6000e10003e000015f00",
              None,
              id="forwards_rjump_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[8] + Op.PUSH1[0] + Op.RJUMPI[7] + Op.RJUMP[5] + Op.PUSH0 + Op.RJUMP[1] + Op.NOT + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000025f6000e100086000e10007e000055fe000011900",
              None,
              id="forwards_rjump_3"
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
