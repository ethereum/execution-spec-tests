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
                    Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=5),
                    Section.Code(code=Op.PUSH0 * 2 + Op.JUMPF[2], code_outputs=5, max_stack_height=2),
                    Section.Code(code=Op.PUSH0 * 3 + Op.RETF, code_outputs=3, max_stack_height=3),
                    ],
              )
              ,
              "ef000101000c02000300040005000404000000008000050005000200030003e30001005f5fe500025f5f5fe4",
              None,
              id="jumpf_compatible_outputs_0"
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
