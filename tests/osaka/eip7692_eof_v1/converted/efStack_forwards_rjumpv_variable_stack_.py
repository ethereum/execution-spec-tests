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
                        name='forwards_rjumpv_variable_stack_0',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(1) + Op.RJUMPV[0] + Op.STOP,
                                max_stack_height=4,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001000f04000000008000045f6000e100025f5f6001e200000000",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_1',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[1] + Op.NOT + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000011900",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_2',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[[2, 3]] + Op.PUSH0 + Op.POP + Op.NOT + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001504000000008000055f6000e100025f5f5f6000e201000200035f501900",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_3',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[1] + Op.PUSH0 + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001104000000008000055f6000e100025f5f5f6000e20000015f00",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_4',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[[1, 2]] + Op.PUSH0 + Op.PUSH0 + Op.NOT + Op.STOP,
                                max_stack_height=6,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001504000000008000065f6000e100025f5f5f6000e201000100025f5f1900",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_5',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[[5, 10]] + Op.PUSH1(1) + Op.RJUMP[7] + Op.PUSH1(2) + Op.RJUMP[2] + Op.PUSH1(3) + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001e04000000008000055f6000e100025f5f5f6000e2010005000a6001e000076002e00002600300",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_6',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[[4, 9]] + Op.PUSH0 + Op.RJUMP[8] + Op.PUSH0 + Op.PUSH0 + Op.RJUMP[3] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.STOP,
                                max_stack_height=7,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001e04000000008000075f6000e100025f5f5f6000e201000400095fe000085f5fe000035f5f5f00",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_7',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[[4, 9]] + Op.POP + Op.RJUMP[8] + Op.POP + Op.POP + Op.RJUMP[3] + Op.POP + Op.POP + Op.POP + Op.STOP,
                                max_stack_height=8,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001002104000000008000085f6000e100025f5f5f5f5f5f6000e2010004000950e000085050e0000350505000",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_8',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[3] + Op.RJUMP[0] + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001304000000008000055f6000e100025f5f5f6000e2000003e0000000",
                    ),
                    Container(
                        name='forwards_rjumpv_variable_stack_9',
                        sections=[
                            Section.Code(
                                code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[2] + Op.PUSH0 + Op.PUSH0 + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPV[4] + Op.PUSH0 + Op.RJUMP[0] + Op.STOP,
                                max_stack_height=5,
                            ),
                        ],
                        expected_bytecode="ef0001010004020001001404000000008000055f6000e100025f5f5f6000e20000045fe0000000",
                    ),
                ],
                ids=lambda x: x.name,
            )
def test_eof_validation(eof_test, container):
    eof_test(container=container)
