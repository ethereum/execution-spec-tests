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
                    name='forwards_rjumpi_0',
                    sections=[
                        Section.Code(
                            code=Op.PUSH1(1) + Op.RJUMPI[0] + Op.STOP,
                            max_stack_height=1,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000604000000008000016001e1000000",
                ),
                Container(
                    name='forwards_rjumpi_1',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.NOT + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000804000000008000025f6000e100011900",
                ),
                Container(
                    name='forwards_rjumpi_10',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[4] + Op.POP + Op.RJUMP[1] + Op.NOT + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000c04000000008000025f6000e1000450e000011900",
                ),
                Container(
                    name='forwards_rjumpi_11',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[3] + Op.RJUMP[0] + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000a04000000008000025f6000e10003e0000000",
                ),
                Container(
                    name='forwards_rjumpi_12',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[0] + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000b04000000008000025f6000e100045fe0000000",
                ),
                Container(
                    name='forwards_rjumpi_2',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[6] + Op.PUSH1(0) + Op.RJUMPI[1] + Op.NOT + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000d04000000008000025f6000e100066000e100011900",
                ),
                Container(
                    name='forwards_rjumpi_3',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.PUSH0 + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000804000000008000025f6000e100015f00",
                ),
                Container(
                    name='forwards_rjumpi_4',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[7] + Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[1] + Op.NOT + Op.STOP,
                            max_stack_height=3,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000e04000000008000035f6000e100075f6000e100011900",
                ),
                Container(
                    name='forwards_rjumpi_5',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(1) + Op.ADD + Op.DUP1 + Op.PUSH1(10) + Op.GT + Op.RJUMPI[4] + Op.DUP1 + Op.RJUMPI[-14] + Op.STOP,
                            max_stack_height=3,
                        ),
                    ],
                    expected_bytecode="ef00010100040200010010 04000000 00800003 5f60010180600a11e1000480e1fff200",
                ),
                Container(
                    name='forwards_rjumpi_6',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(1) +  Op.ADD + Op.DUP1 + Op.PUSH1(10) + Op.GT + Op.RJUMPI[5] + Op.PUSH0 + Op.DUP1 + Op.RJUMPI[-13] + Op.STOP,
                            max_stack_height=3,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001001104000000008000035f60010180600a11e100055f80e1fff300",
                ),
                Container(
                    name='forwards_rjumpi_7',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[1] + Op.PUSH0 + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000c04000000008000025f6000e100045fe000015f00",
                ),
                Container(
                    name='forwards_rjumpi_8',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[4] + Op.PUSH0 + Op.RJUMP[1] + Op.NOT + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000c04000000008000025f6000e100045fe000011900",
                ),
                Container(
                    name='forwards_rjumpi_9',
                    sections=[
                        Section.Code(
                            code=Op.PUSH0 + Op.PUSH1(0) + Op.RJUMPI[4] + Op.POP + Op.RJUMP[1] + Op.POP + Op.STOP,
                            max_stack_height=2,
                        ),
                    ],
                    expected_bytecode="ef0001010004020001000c04000000008000025f6000e1000450e000015000",
                ),
            ],
            ids=lambda x: x.name,
        )
def test_eof_validation(eof_test, container):
    eof_test(container=container)
