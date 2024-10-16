""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6206.md"
REFERENCE_SPEC_VERSION = "c97849460824210bc5db0b00af87aaa0b5a07346"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
                    Section.Code(code=Op.JUMPF[2], code_outputs=3, max_stack_height=0),
                    Section.Code(code=Op.PUSH0 * 5 + Op.RETF, code_outputs=5, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040003000604000000008000030003000000050003e3000100e500025f5f5f5f5fe4",
              EOFException.JUMPF_DESTINATION_INCOMPATIBLE_OUTPUTS,
              id="jumpf_incompatible_outputs_0"
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
