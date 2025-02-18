import pytest
from ethereum_test_exceptions import EOFException
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = 'EIPS/eip-663.md'
REFERENCE_SPEC_VERSION = 'b658bb87fe039d29e9475d5cfaebca9b92e0fca2'

@pytest.mark.parametrize(
      'container',
      [
          Container(
              name='backwards_rjumpv_0',
              sections=[
                  Section.Code(
                      code=Op.PUSH1(0) + Op.RJUMPV[-6] + Op.STOP,
                      max_stack_height=1,
                  ),
              ],
              expected_bytecode="ef0001010004020001000704000000008000016000e200fffa00",
          ),
          Container(
              name='backwards_rjumpv_1',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.STOP,
                      max_stack_height=1,
                  ),
              ],
              expected_bytecode="ef0001010004020001000904000000008000015f506000e200fff800",
          ),
          Container(
              name='backwards_rjumpv_2',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH1(0) + Op.RJUMPV[-14] + Op.STOP,
                      max_stack_height=1,
                  ),
              ],
              expected_bytecode="ef0001010004020001000f04000000008000015f506000e200fff86000e200fff200",
          ),
          Container(
              name='backwards_rjumpv_3',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[-15] + Op.STOP,
                      max_stack_height=2,
                  ),
              ],
              expected_bytecode="ef0001010004020001001004000000008000025f506000e200fff85f6000e200fff100",
              validity_error=EOFException.STACK_HEIGHT_MISMATCH,
          ),
          Container(
              name='backwards_rjumpv_4',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.RJUMP[-11],
                      max_stack_height=1,
                  ),
              ],
              expected_bytecode="ef0001010004020001000b04000000008000015f506000e200fff8e0fff5",
          ),
          Container(
              name='backwards_rjumpv_5',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH0 + Op.RJUMP[-12],
                      max_stack_height=1,
                  ),
              ],
              expected_bytecode="ef0001010004020001000c04000000008000015f506000e200fff85fe0fff4",
              validity_error=EOFException.STACK_HEIGHT_MISMATCH,
          ),
          Container(
              name='backwards_rjumpv_6',
              sections=[
                  Section.Code(
                      code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[-12] + Op.STOP,
                      max_stack_height=3,
                  ),
              ],
              expected_bytecode="ef0001010004020001000e04000000008000035f6000e100015f6000e200fff400",
              validity_error=EOFException.STACK_HEIGHT_MISMATCH,
          ),
          Container(
              name='backwards_rjumpv_7',
              sections=[
                  Section.Code(
                      code=Op.PUSH1[190] + Op.PUSH1(0) + Op.RJUMPI[1] + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-12] + Op.STOP,
                      max_stack_height=3,
                  ),
              ],
              expected_bytecode="ef0001010004020001000f040000000080000360be6000e10001506000e200fff400",
              validity_error=EOFException.STACK_HEIGHT_MISMATCH,
          ),
      ],
      ids=lambda x: x.name,
  )
def test_eof_validation(eof_test, container):
    eof_test(container=container)
