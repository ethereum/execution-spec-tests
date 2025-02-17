import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-663.md"
REFERENCE_SPEC_VERSION = "b658bb87fe039d29e9475d5cfaebca9b92e0fca2"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="backwards_rjump_1",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.POP + Op.RJUMP[-5],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000504000000008000015f50e0fffb",
        ),
        Container(
            name="backwards_rjump_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.POP
                    + Op.PUSH1(1)
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.RJUMP[-11],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000015f506001e10003e0fff8e0fff5",
        ),
        Container(
            name="backwards_rjump_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.POP
                    + Op.PUSH1(1)
                    + Op.RJUMPI[3]
                    + Op.RJUMP[-8]
                    + Op.PUSH0
                    + Op.RJUMP[-12],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000015f506001e10003e0fff85fe0fff4",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name="backwards_rjump_4",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RJUMP[-4],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000404000000008000015fe0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
        Container(
            name="backwards_rjump_5",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.POP + Op.RJUMP[-4],
                    max_stack_height=1,
                ),
            ],
            expected_bytecode="ef0001010004020001000504000000008000015f50e0fffc",
            validity_error=EOFException.STACK_HEIGHT_MISMATCH,
        ),
    ],
    ids=lambda x: x.name,
)
def test_eof_validation(eof_test, container):
    eof_test(container=container)
