""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, UndefinedOpcodes as UOp, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "12ca2f0bd2f7380100e154aaaa0995c46cbb2710"
Op.NOP = Op.JUMPDEST

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef00010100040200010013040000000080001160018080808080808080808080808080808000",
              None,
              id="eof1_undefined_opcodes_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.ADD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800100",
              None,
              id="eof1_undefined_opcodes_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MUL + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800200",
              None,
              id="eof1_undefined_opcodes_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SUB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800300",
              None,
              id="eof1_undefined_opcodes_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DIV + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800400",
              None,
              id="eof1_undefined_opcodes_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SDIV + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800500",
              None,
              id="eof1_undefined_opcodes_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MOD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800600",
              None,
              id="eof1_undefined_opcodes_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SMOD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800700",
              None,
              id="eof1_undefined_opcodes_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.ADDMOD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800800",
              None,
              id="eof1_undefined_opcodes_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MULMOD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800900",
              None,
              id="eof1_undefined_opcodes_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.EXP + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800a00",
              None,
              id="eof1_undefined_opcodes_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SIGNEXTEND + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800b00",
              None,
              id="eof1_undefined_opcodes_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_0C + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800c00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_12"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0014',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_0D + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800d00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_13"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0015',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_0E + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800e00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_14"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0016',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_0F + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080800f00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_15"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0017',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LT + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801000",
              None,
              id="eof1_undefined_opcodes_16"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0018',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.GT + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801100",
              None,
              id="eof1_undefined_opcodes_17"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0019',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SLT + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801200",
              None,
              id="eof1_undefined_opcodes_18"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0020',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SGT + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801300",
              None,
              id="eof1_undefined_opcodes_19"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0021',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.EQ + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801400",
              None,
              id="eof1_undefined_opcodes_20"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0022',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.ISZERO + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801500",
              None,
              id="eof1_undefined_opcodes_21"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0023',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.AND + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801600",
              None,
              id="eof1_undefined_opcodes_22"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0024',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.OR + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801700",
              None,
              id="eof1_undefined_opcodes_23"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0025',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.XOR + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801800",
              None,
              id="eof1_undefined_opcodes_24"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0026',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.NOT + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801900",
              None,
              id="eof1_undefined_opcodes_25"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0027',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BYTE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801a00",
              None,
              id="eof1_undefined_opcodes_26"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0028',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SHL + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801b00",
              None,
              id="eof1_undefined_opcodes_27"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0029',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SHR + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801c00",
              None,
              id="eof1_undefined_opcodes_28"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0030',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SAR + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801d00",
              None,
              id="eof1_undefined_opcodes_29"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0031',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_1E + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801e00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_30"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0032',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_1F + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080801f00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_31"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0033',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SHA3 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802000",
              None,
              id="eof1_undefined_opcodes_32"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0034',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_21 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802100",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_33"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0035',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_22 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802200",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_34"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0036',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_23 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802300",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_35"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0037',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_24 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802400",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_36"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0038',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_25 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802500",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_37"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0039',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_26 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_38"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0040',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_27 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802700",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_39"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0041',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_28 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802800",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_40"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0042',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_29 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_41"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0043',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2A + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802a00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_42"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0044',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2B + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802b00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_43"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0045',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2C + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802c00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_44"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0046',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2D + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802d00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_45"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0047',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2E + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802e00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_46"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0048',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_2F + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080802f00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_47"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0049',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.ADDRESS + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803000",
              None,
              id="eof1_undefined_opcodes_48"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0050',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BALANCE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080803100",
              None,
              id="eof1_undefined_opcodes_49"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0051',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.ORIGIN + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803200",
              None,
              id="eof1_undefined_opcodes_50"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0052',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CALLER + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803300",
              None,
              id="eof1_undefined_opcodes_51"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0053',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CALLVALUE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803400",
              None,
              id="eof1_undefined_opcodes_52"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0054',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CALLDATALOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080803500",
              None,
              id="eof1_undefined_opcodes_53"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0055',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CALLDATASIZE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803600",
              None,
              id="eof1_undefined_opcodes_54"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0056',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CALLDATACOPY + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080803700",
              None,
              id="eof1_undefined_opcodes_55"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0057',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.GASPRICE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803a00",
              None,
              id="eof1_undefined_opcodes_56"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0058',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.RETURNDATASIZE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080803d00",
              None,
              id="eof1_undefined_opcodes_57"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0059',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.RETURNDATACOPY + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080803e00",
              None,
              id="eof1_undefined_opcodes_58"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0060',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BLOCKHASH + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804000",
              None,
              id="eof1_undefined_opcodes_59"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0061',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.COINBASE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804100",
              None,
              id="eof1_undefined_opcodes_60"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0062',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.TIMESTAMP + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804200",
              None,
              id="eof1_undefined_opcodes_61"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0063',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.NUMBER + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804300",
              None,
              id="eof1_undefined_opcodes_62"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0064',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.PREVRANDAO + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804400",
              None,
              id="eof1_undefined_opcodes_63"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0065',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.GASLIMIT + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804500",
              None,
              id="eof1_undefined_opcodes_64"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0066',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.CHAINID + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804600",
              None,
              id="eof1_undefined_opcodes_65"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0067',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SELFBALANCE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804700",
              None,
              id="eof1_undefined_opcodes_66"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0068',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BASEFEE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804800",
              None,
              id="eof1_undefined_opcodes_67"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0069',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BLOBHASH + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804900",
              None,
              id="eof1_undefined_opcodes_68"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0070',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.BLOBBASEFEE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080804a00",
              None,
              id="eof1_undefined_opcodes_69"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0071',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_4B + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804b00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_70"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0072',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_4C + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804c00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_71"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0073',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_4D + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804d00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_72"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0074',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_4E + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804e00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_73"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0075',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_4F + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080804f00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_74"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0076',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.POP + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805000",
              None,
              id="eof1_undefined_opcodes_75"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0077',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MLOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805100",
              None,
              id="eof1_undefined_opcodes_76"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0078',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MSTORE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805200",
              None,
              id="eof1_undefined_opcodes_77"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0079',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MSTORE8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805300",
              None,
              id="eof1_undefined_opcodes_78"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0080',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SLOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805400",
              None,
              id="eof1_undefined_opcodes_79"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0081',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SSTORE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805500",
              None,
              id="eof1_undefined_opcodes_80"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0082',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MSIZE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080805900",
              None,
              id="eof1_undefined_opcodes_81"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0083',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.NOP + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805b00",
              None,
              id="eof1_undefined_opcodes_82"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0084',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.TLOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805c00",
              None,
              id="eof1_undefined_opcodes_83"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0085',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.TSTORE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805d00",
              None,
              id="eof1_undefined_opcodes_84"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0086',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.MCOPY + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080805e00",
              None,
              id="eof1_undefined_opcodes_85"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0087',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.PUSH0 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080805f00",
              None,
              id="eof1_undefined_opcodes_86"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0088',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 17 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808000",
              None,
              id="eof1_undefined_opcodes_87"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0089',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP2 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808100",
              None,
              id="eof1_undefined_opcodes_88"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0090',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP3 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808200",
              None,
              id="eof1_undefined_opcodes_89"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0091',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP4 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808300",
              None,
              id="eof1_undefined_opcodes_90"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0092',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP5 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808400",
              None,
              id="eof1_undefined_opcodes_91"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0093',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP6 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808500",
              None,
              id="eof1_undefined_opcodes_92"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0094',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP7 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808600",
              None,
              id="eof1_undefined_opcodes_93"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0095',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP8 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808700",
              None,
              id="eof1_undefined_opcodes_94"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0096',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP9 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808800",
              None,
              id="eof1_undefined_opcodes_95"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0097',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP10 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808900",
              None,
              id="eof1_undefined_opcodes_96"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0098',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP11 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808a00",
              None,
              id="eof1_undefined_opcodes_97"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0099',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP12 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808b00",
              None,
              id="eof1_undefined_opcodes_98"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0100',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP13 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808c00",
              None,
              id="eof1_undefined_opcodes_99"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0101',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP14 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808d00",
              None,
              id="eof1_undefined_opcodes_100"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0102',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP15 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808e00",
              None,
              id="eof1_undefined_opcodes_101"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0103',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DUP16 + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000126001808080808080808080808080808080808f00",
              None,
              id="eof1_undefined_opcodes_102"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0104',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP1 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809000",
              None,
              id="eof1_undefined_opcodes_103"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0105',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP2 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809100",
              None,
              id="eof1_undefined_opcodes_104"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0106',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP3 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809200",
              None,
              id="eof1_undefined_opcodes_105"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0107',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP4 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809300",
              None,
              id="eof1_undefined_opcodes_106"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0108',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP5 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809400",
              None,
              id="eof1_undefined_opcodes_107"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0109',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809500",
              None,
              id="eof1_undefined_opcodes_108"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0110',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP7 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809600",
              None,
              id="eof1_undefined_opcodes_109"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0111',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809700",
              None,
              id="eof1_undefined_opcodes_110"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0112',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809800",
              None,
              id="eof1_undefined_opcodes_111"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0113',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP10 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809900",
              None,
              id="eof1_undefined_opcodes_112"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0114',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP11 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809a00",
              None,
              id="eof1_undefined_opcodes_113"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0115',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP12 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809b00",
              None,
              id="eof1_undefined_opcodes_114"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0116',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP13 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809c00",
              None,
              id="eof1_undefined_opcodes_115"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0117',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP14 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809d00",
              None,
              id="eof1_undefined_opcodes_116"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0118',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP15 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809e00",
              None,
              id="eof1_undefined_opcodes_117"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0119',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.SWAP16 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000116001808080808080808080808080808080809f00",
              None,
              id="eof1_undefined_opcodes_118"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0120',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LOG0 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a000",
              None,
              id="eof1_undefined_opcodes_119"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0121',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LOG1 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a100",
              None,
              id="eof1_undefined_opcodes_120"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0122',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LOG2 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a200",
              None,
              id="eof1_undefined_opcodes_121"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0123',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LOG3 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a300",
              None,
              id="eof1_undefined_opcodes_122"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0124',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.LOG4 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a400",
              None,
              id="eof1_undefined_opcodes_123"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0125',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_A5 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a500",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_124"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0126',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_A6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_125"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0127',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_A7 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a700",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_126"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0128',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_A8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a800",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_127"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0129',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_A9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080a900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_128"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0130',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AA + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080aa00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_129"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0131',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ab00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_130"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0132',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AC + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ac00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_131"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0133',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ad00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_132"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0134',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ae00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_133"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0135',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_AF + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080af00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_134"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0136',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B0 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b000",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_135"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0137',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B1 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b100",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_136"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0138',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B2 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b200",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_137"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0139',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B3 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b300",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_138"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0140',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B4 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b400",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_139"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0141',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B5 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b500",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_140"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0142',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_141"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0143',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B7 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b700",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_142"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0144',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b800",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_143"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0145',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_B9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080b900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_144"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0146',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BA + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ba00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_145"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0147',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080bb00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_146"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0148',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BC + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080bc00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_147"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0149',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080bd00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_148"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0150',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080be00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_149"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0151',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_BF + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080bf00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_150"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0152',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C0 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c000",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_151"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0153',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C1 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c100",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_152"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0154',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C2 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c200",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_153"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0155',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C3 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c300",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_154"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0156',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C4 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c400",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_155"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0157',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C5 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c500",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_156"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0158',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_157"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0159',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C7 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c700",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_158"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0160',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c800",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_159"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0161',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_C9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080c900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_160"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0162',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CA + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ca00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_161"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0163',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080cb00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_162"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0164',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CC + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080cc00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_163"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0165',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080cd00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_164"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0166',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ce00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_165"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0167',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_CF + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080cf00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_166"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0168',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DATALOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d000",
              None,
              id="eof1_undefined_opcodes_167"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0169',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DATASIZE + Op.STOP, max_stack_height=18),
                    ],
              )
              ,
              "ef000101000402000100140400000000800012600180808080808080808080808080808080d200",
              None,
              id="eof1_undefined_opcodes_168"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0170',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.DATACOPY + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d300",
              None,
              id="eof1_undefined_opcodes_169"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0171',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D4 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d400",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_170"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0172',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D5 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d500",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_171"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0173',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_172"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0174',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D7 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d700",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_173"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0175',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D8 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d800",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_174"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0176',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_D9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080d900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_175"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0177',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DA + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080da00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_176"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0178',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080db00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_177"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0179',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DC + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080dc00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_178"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0180',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080dd00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_179"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0181',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DE + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080de00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_180"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0182',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_DF + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080df00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_181"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0184',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_E9 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080e900",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_183"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0185',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_EA + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ea00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_184"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0186',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_EB + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080eb00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_185"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0187',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_ED + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ed00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_186"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0188',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_EF + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080ef00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_187"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0189',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.RETURN, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100130400000000800011600180808080808080808080808080808080f3",
              None,
              id="eof1_undefined_opcodes_188"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0190',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_F6 + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080f600",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_189"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0191',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.RETURNDATALOAD + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080f700",
              None,
              id="eof1_undefined_opcodes_190"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0192',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.EXTCALL + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080f800",
              None,
              id="eof1_undefined_opcodes_191"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0193',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.EXTDELEGATECALL + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080f900",
              None,
              id="eof1_undefined_opcodes_192"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0194',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.EXTSTATICCALL + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080fb00",
              None,
              id="eof1_undefined_opcodes_193"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0195',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + UOp.OPCODE_FC + Op.STOP, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100140400000000800011600180808080808080808080808080808080fc00",
              EOFException.UNDEFINED_INSTRUCTION,
              id="eof1_undefined_opcodes_194"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0196',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.REVERT, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100130400000000800011600180808080808080808080808080808080fd",
              None,
              id="eof1_undefined_opcodes_195"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0197',
                sections = [
                    Section.Code(code=Op.PUSH1[1] + Op.DUP1 * 16 + Op.INVALID, max_stack_height=17),
                    ],
              )
              ,
              "ef000101000402000100130400000000800011600180808080808080808080808080808080fe",
              None,
              id="eof1_undefined_opcodes_196"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0198',
                sections = [
                    Section.Code(code=Op.INVALID, max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100010400000000800000fe",
              None,
              id="eof1_undefined_opcodes_197"
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
