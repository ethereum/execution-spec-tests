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
               name='backwards_rjumpv_variable_stack_0',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[-6] + Op.STOP,
                       max_stack_height=4,
                   ),
               ],
               expected_bytecode="ef0001010004020001000f04000000008000045f6000e100025f5f6000e200fffa00",
           ),
           Container(
               name='backwards_rjumpv_variable_stack_1',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.STOP,
                       max_stack_height=4,
                   ),
               ],
               expected_bytecode="ef0001010004020001001104000000008000045f6000e100025f5f5f506000e200fff800",
           ),
           Container(
               name='backwards_rjumpv_variable_stack_2',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH1(0) + Op.RJUMPV[-14] + Op.STOP,
                       max_stack_height=4,
                   ),
               ],
               expected_bytecode="ef0001010004020001001704000000008000045f6000e100025f5f5f506000e200fff86000e200fff200",
           ),
           Container(
               name='backwards_rjumpv_variable_stack_3',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[-15] + Op.STOP,
                       max_stack_height=5,
                   ),
               ],
               expected_bytecode="ef0001010004020001001804000000008000055f6000e100025f5f5f506000e200fff85f6000e200fff100",
               validity_error=EOFException.STACK_HEIGHT_MISMATCH,
           ),
           Container(
               name='backwards_rjumpv_variable_stack_4',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.RJUMP[-11],
                       max_stack_height=4,
                   ),
               ],
               expected_bytecode="ef0001010004020001001304000000008000045f6000e100025f5f5f506000e200fff8e0fff5",
           ),
           Container(
               name='backwards_rjumpv_variable_stack_5',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-8] + Op.PUSH0 + Op.RJUMP[-12],
                       max_stack_height=4,
                   ),
               ],
               expected_bytecode="ef0001010004020001001404000000008000045f6000e100025f5f5f506000e200fff85fe0fff4",
               validity_error=EOFException.STACK_HEIGHT_MISMATCH,
           ),
           Container(
               name='backwards_rjumpv_variable_stack_6',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[-12] + Op.STOP,
                       max_stack_height=5,
                   ),
               ],
               expected_bytecode="ef0001010004020001001604000000008000055f6000e100025f5f5f6000e100015f6000e200fff400",
               validity_error=EOFException.STACK_HEIGHT_MISMATCH,
           ),
           Container(
               name='backwards_rjumpv_variable_stack_7',
               sections=[
                   Section.Code(
                       code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.POP + Op.PUSH1(0) + Op.RJUMPV[-12] + Op.STOP,
                       max_stack_height=5,
                   ),
               ],
               expected_bytecode="ef0001010004020001001704000000008000055f6000e100025f5f5f5f6000e10001506000e200fff400",
               validity_error=EOFException.STACK_HEIGHT_MISMATCH,
           ),
       ],
       ids=lambda x: x.name,
   )
def test_eof_validation(eof_test, container):
    eof_test(container=container)
