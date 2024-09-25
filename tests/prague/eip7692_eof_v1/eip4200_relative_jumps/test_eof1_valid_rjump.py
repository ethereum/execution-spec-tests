""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4200.md"
REFERENCE_SPEC_VERSION = "b452cf8a47e5b5bf08a1576a4dfaf828306beb5a"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.NOP + Op.RJUMP[-4], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000005be0fffc",
              None,
              id="offset_negative"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH0 + Op.RJUMPI[5] + Op.PUSH0 * 2 + Op.RJUMP[3] + Op.PUSH0 + Op.PUSH1[1] + Op.STOP, max_stack_height=2),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000025fe100055f5fe000035f600100",
              None,
              id="offset_positive"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.RJUMP[0] + Op.STOP, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100040400000000800000e0000000",
              None,
              id="offset_zero"
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
