""""
EOF v1 validation code - Exported from evmone unit tests
"""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "12ca2f0bd2f7380100e154aaaa0995c46cbb2710"

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        pytest.param(
              Container(
                name = 'EOFV1_0001',
                sections = [
                    Section.Code(code=[0x60], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000060",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_0"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0002',
                sections = [
                    Section.Code(code=Op.PUSH1[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100030400000000800001600000",
              None,
              id="eof1_truncated_push_1"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0003',
                sections = [
                    Section.Code(code=[0x61], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000061",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_2"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0004',
                sections = [
                    Section.Code(code=[0x61, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006100",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_3"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0005',
                sections = [
                    Section.Code(code=Op.PUSH2[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000161000000",
              None,
              id="eof1_truncated_push_4"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0006',
                sections = [
                    Section.Code(code=[0x62], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000062",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_5"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0007',
                sections = [
                    Section.Code(code=[0x62, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006200",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_6"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0008',
                sections = [
                    Section.Code(code=[0x62, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000620000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_7"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0009',
                sections = [
                    Section.Code(code=Op.PUSH3[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000016200000000",
              None,
              id="eof1_truncated_push_8"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0010',
                sections = [
                    Section.Code(code=[0x63], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000063",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_9"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0011',
                sections = [
                    Section.Code(code=[0x63, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006300",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_10"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0012',
                sections = [
                    Section.Code(code=[0x63, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000630000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_11"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0013',
                sections = [
                    Section.Code(code=[0x63, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000063000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_12"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0014',
                sections = [
                    Section.Code(code=Op.PUSH4[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100060400000000800001630000000000",
              None,
              id="eof1_truncated_push_13"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0015',
                sections = [
                    Section.Code(code=[0x64], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000064",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_14"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0016',
                sections = [
                    Section.Code(code=[0x64, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006400",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_15"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0017',
                sections = [
                    Section.Code(code=[0x64, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000640000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_16"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0018',
                sections = [
                    Section.Code(code=[0x64, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000064000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_17"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0019',
                sections = [
                    Section.Code(code=[0x64, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006400000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_18"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0020',
                sections = [
                    Section.Code(code=Op.PUSH5[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000164000000000000",
              None,
              id="eof1_truncated_push_19"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0021',
                sections = [
                    Section.Code(code=[0x65], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000065",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_20"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0022',
                sections = [
                    Section.Code(code=[0x65, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006500",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_21"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0023',
                sections = [
                    Section.Code(code=[0x65, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000650000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_22"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0024',
                sections = [
                    Section.Code(code=[0x65, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000065000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_23"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0025',
                sections = [
                    Section.Code(code=[0x65, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006500000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_24"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0026',
                sections = [
                    Section.Code(code=[0x65, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000650000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_25"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0027',
                sections = [
                    Section.Code(code=Op.PUSH6[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000016500000000000000",
              None,
              id="eof1_truncated_push_26"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0028',
                sections = [
                    Section.Code(code=[0x66], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000066",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_27"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0029',
                sections = [
                    Section.Code(code=[0x66, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006600",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_28"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0030',
                sections = [
                    Section.Code(code=[0x66, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000660000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_29"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0031',
                sections = [
                    Section.Code(code=[0x66, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000066000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_30"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0032',
                sections = [
                    Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006600000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_31"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0033',
                sections = [
                    Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000660000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_32"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0034',
                sections = [
                    Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000066000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_33"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0035',
                sections = [
                    Section.Code(code=Op.PUSH7[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100090400000000800001660000000000000000",
              None,
              id="eof1_truncated_push_34"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0036',
                sections = [
                    Section.Code(code=[0x67], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000067",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_35"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0037',
                sections = [
                    Section.Code(code=[0x67, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006700",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_36"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0038',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000670000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_37"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0039',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000067000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_38"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0040',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006700000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_39"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0041',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000670000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_40"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0042',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000067000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_41"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0043',
                sections = [
                    Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006700000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_42"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0044',
                sections = [
                    Section.Code(code=Op.PUSH8[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000167000000000000000000",
              None,
              id="eof1_truncated_push_43"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0045',
                sections = [
                    Section.Code(code=[0x68], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000068",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_44"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0046',
                sections = [
                    Section.Code(code=[0x68, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006800",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_45"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0047',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000680000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_46"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0048',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000068000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_47"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0049',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006800000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_48"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0050',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000680000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_49"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0051',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000068000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_50"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0052',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006800000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_51"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0053',
                sections = [
                    Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000680000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_52"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0054',
                sections = [
                    Section.Code(code=Op.PUSH9[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000016800000000000000000000",
              None,
              id="eof1_truncated_push_53"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0055',
                sections = [
                    Section.Code(code=[0x69], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000069",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_54"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0056',
                sections = [
                    Section.Code(code=[0x69, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006900",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_55"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0057',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000690000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_56"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0058',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000069000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_57"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0059',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006900000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_58"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0060',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000690000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_59"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0061',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000069000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_60"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0062',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006900000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_61"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0063',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000690000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_62"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0064',
                sections = [
                    Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000069000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_63"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0065',
                sections = [
                    Section.Code(code=Op.PUSH10[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800001690000000000000000000000",
              None,
              id="eof1_truncated_push_64"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0066',
                sections = [
                    Section.Code(code=[0x6a], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006a",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_65"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0067',
                sections = [
                    Section.Code(code=[0x6a, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006a00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_66"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0068',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006a0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_67"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0069',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006a000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_68"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0070',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006a00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_69"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0071',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006a0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_70"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0072',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006a000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_71"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0073',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006a00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_72"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0074',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006a0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_73"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0075',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006a000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_74"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0076',
                sections = [
                    Section.Code(code=[0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006a00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_75"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0077',
                sections = [
                    Section.Code(code=Op.PUSH11[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000016a000000000000000000000000",
              None,
              id="eof1_truncated_push_76"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0078',
                sections = [
                    Section.Code(code=[0x6b], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006b",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_77"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0079',
                sections = [
                    Section.Code(code=[0x6b, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006b00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_78"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0080',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006b0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_79"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0081',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006b000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_80"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0082',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006b00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_81"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0083',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006b0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_82"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0084',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006b000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_83"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0085',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006b00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_84"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0086',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006b0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_85"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0087',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006b000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_86"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0088',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006b00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_87"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0089',
                sections = [
                    Section.Code(code=[0x6b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000006b0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_88"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0090',
                sections = [
                    Section.Code(code=Op.PUSH12[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000016b00000000000000000000000000",
              None,
              id="eof1_truncated_push_89"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0091',
                sections = [
                    Section.Code(code=[0x6c], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006c",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_90"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0092',
                sections = [
                    Section.Code(code=[0x6c, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006c00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_91"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0093',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006c0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_92"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0094',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006c000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_93"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0095',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006c00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_94"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0096',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006c0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_95"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0097',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006c000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_96"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0098',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006c00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_97"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0099',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006c0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_98"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0100',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006c000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_99"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0101',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006c00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_100"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0102',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000006c0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_101"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0103',
                sections = [
                    Section.Code(code=[0x6c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000006c000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_102"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0104',
                sections = [
                    Section.Code(code=Op.PUSH13[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000016c0000000000000000000000000000",
              None,
              id="eof1_truncated_push_103"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0105',
                sections = [
                    Section.Code(code=[0x6d], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006d",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_104"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0106',
                sections = [
                    Section.Code(code=[0x6d, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006d00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_105"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0107',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006d0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_106"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0108',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006d000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_107"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0109',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006d00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_108"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0110',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006d0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_109"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0111',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006d000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_110"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0112',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006d00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_111"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0113',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006d0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_112"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0114',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006d000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_113"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0115',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006d00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_114"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0116',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000006d0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_115"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0117',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000006d000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_116"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0118',
                sections = [
                    Section.Code(code=[0x6d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000006d00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_117"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0119',
                sections = [
                    Section.Code(code=Op.PUSH14[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000016d000000000000000000000000000000",
              None,
              id="eof1_truncated_push_118"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0120',
                sections = [
                    Section.Code(code=[0x6e], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006e",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_119"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0121',
                sections = [
                    Section.Code(code=[0x6e, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006e00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_120"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0122',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006e0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_121"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0123',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006e000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_122"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0124',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006e00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_123"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0125',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006e0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_124"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0126',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006e000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_125"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0127',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006e00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_126"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0128',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006e0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_127"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0129',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006e000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_128"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0130',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006e00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_129"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0131',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000006e0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_130"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0132',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000006e000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_131"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0133',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000006e00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_132"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0134',
                sections = [
                    Section.Code(code=[0x6e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000006e0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_133"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0135',
                sections = [
                    Section.Code(code=Op.PUSH15[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000016e00000000000000000000000000000000",
              None,
              id="eof1_truncated_push_134"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0136',
                sections = [
                    Section.Code(code=[0x6f], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000006f",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_135"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0137',
                sections = [
                    Section.Code(code=[0x6f, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000006f00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_136"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0138',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000006f0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_137"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0139',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000006f000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_138"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0140',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000006f00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_139"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0141',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000006f0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_140"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0142',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000006f000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_141"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0143',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000006f00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_142"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0144',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000006f0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_143"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0145',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000006f000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_144"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0146',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000006f00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_145"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0147',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000006f0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_146"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0148',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000006f000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_147"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0149',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000006f00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_148"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0150',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000006f0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_149"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0151',
                sections = [
                    Section.Code(code=[0x6f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000006f000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_150"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0152',
                sections = [
                    Section.Code(code=Op.PUSH16[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000016f0000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_151"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0153',
                sections = [
                    Section.Code(code=[0x70], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000070",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_152"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0154',
                sections = [
                    Section.Code(code=[0x70, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_153"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0155',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000700000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_154"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0156',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000070000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_155"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0157',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_156"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0158',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000700000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_157"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0159',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000070000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_158"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0160',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_159"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0161',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000700000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_160"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0162',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000070000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_161"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0163',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_162"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0164',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000700000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_163"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0165',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000070000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_164"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0166',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_165"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0167',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000700000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_166"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0168',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000070000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_167"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0169',
                sections = [
                    Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_168"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0170',
                sections = [
                    Section.Code(code=Op.PUSH17[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000170000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_169"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0171',
                sections = [
                    Section.Code(code=[0x71], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000071",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_170"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0172',
                sections = [
                    Section.Code(code=[0x71, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007100",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_171"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0173',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000710000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_172"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0174',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000071000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_173"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0175',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007100000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_174"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0176',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000710000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_175"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0177',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000071000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_176"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0178',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007100000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_177"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0179',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000710000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_178"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0180',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000071000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_179"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0181',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007100000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_180"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0182',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000710000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_181"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0183',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000071000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_182"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0184',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007100000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_183"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0185',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000710000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_184"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0186',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000071000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_185"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0187',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007100000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_186"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0188',
                sections = [
                    Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000710000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_187"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0189',
                sections = [
                    Section.Code(code=Op.PUSH18[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000017100000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_188"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0190',
                sections = [
                    Section.Code(code=[0x72], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000072",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_189"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0191',
                sections = [
                    Section.Code(code=[0x72, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007200",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_190"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0192',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000720000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_191"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0193',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000072000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_192"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0194',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007200000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_193"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0195',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000720000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_194"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0196',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000072000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_195"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0197',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007200000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_196"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0198',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000720000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_197"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0199',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000072000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_198"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0200',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007200000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_199"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0201',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000720000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_200"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0202',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000072000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_201"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0203',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007200000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_202"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0204',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000720000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_203"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0205',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000072000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_204"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0206',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007200000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_205"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0207',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000720000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_206"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0208',
                sections = [
                    Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000072000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_207"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0209',
                sections = [
                    Section.Code(code=Op.PUSH19[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100150400000000800001720000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_208"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0210',
                sections = [
                    Section.Code(code=[0x73], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000073",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_209"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0211',
                sections = [
                    Section.Code(code=[0x73, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007300",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_210"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0212',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000730000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_211"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0213',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000073000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_212"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0214',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007300000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_213"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0215',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000730000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_214"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0216',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000073000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_215"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0217',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007300000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_216"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0218',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000730000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_217"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0219',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000073000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_218"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0220',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007300000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_219"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0221',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000730000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_220"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0222',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000073000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_221"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0223',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007300000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_222"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0224',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000730000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_223"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0225',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000073000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_224"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0226',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007300000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_225"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0227',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000730000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_226"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0228',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000073000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_227"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0229',
                sections = [
                    Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007300000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_228"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0230',
                sections = [
                    Section.Code(code=Op.PUSH20[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000173000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_229"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0231',
                sections = [
                    Section.Code(code=[0x74], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000074",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_230"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0232',
                sections = [
                    Section.Code(code=[0x74, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007400",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_231"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0233',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000740000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_232"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0234',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000074000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_233"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0235',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007400000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_234"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0236',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000740000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_235"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0237',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000074000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_236"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0238',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007400000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_237"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0239',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000740000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_238"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0240',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000074000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_239"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0241',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007400000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_240"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0242',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000740000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_241"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0243',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000074000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_242"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0244',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007400000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_243"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0245',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000740000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_244"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0246',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000074000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_245"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0247',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007400000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_246"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0248',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000740000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_247"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0249',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000074000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_248"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0250',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007400000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_249"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0251',
                sections = [
                    Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000740000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_250"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0252',
                sections = [
                    Section.Code(code=Op.PUSH21[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000017400000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_251"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0253',
                sections = [
                    Section.Code(code=[0x75], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000075",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_252"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0254',
                sections = [
                    Section.Code(code=[0x75, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007500",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_253"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0255',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000750000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_254"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0256',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000075000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_255"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0257',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007500000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_256"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0258',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000750000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_257"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0259',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000075000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_258"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0260',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007500000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_259"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0261',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000750000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_260"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0262',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000075000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_261"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0263',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007500000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_262"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0264',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000750000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_263"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0265',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000075000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_264"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0266',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007500000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_265"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0267',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000750000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_266"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0268',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000075000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_267"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0269',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007500000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_268"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0270',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000750000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_269"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0271',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000075000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_270"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0272',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007500000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_271"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0273',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000750000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_272"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0274',
                sections = [
                    Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000075000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_273"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0275',
                sections = [
                    Section.Code(code=Op.PUSH22[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef000101000402000100180400000000800001750000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_274"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0276',
                sections = [
                    Section.Code(code=[0x76], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000076",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_275"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0277',
                sections = [
                    Section.Code(code=[0x76, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007600",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_276"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0278',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000760000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_277"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0279',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000076000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_278"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0280',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007600000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_279"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0281',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000760000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_280"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0282',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000076000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_281"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0283',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007600000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_282"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0284',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000760000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_283"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0285',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000076000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_284"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0286',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007600000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_285"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0287',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000760000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_286"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0288',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000076000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_287"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0289',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007600000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_288"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0290',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000760000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_289"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0291',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000076000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_290"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0292',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007600000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_291"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0293',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000760000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_292"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0294',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000076000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_293"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0295',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007600000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_294"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0296',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000760000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_295"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0297',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000076000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_296"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0298',
                sections = [
                    Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007600000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_297"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0299',
                sections = [
                    Section.Code(code=Op.PUSH23[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef00010100040200010019040000000080000176000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_298"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0300',
                sections = [
                    Section.Code(code=[0x77], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000077",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_299"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0301',
                sections = [
                    Section.Code(code=[0x77, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007700",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_300"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0302',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000770000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_301"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0303',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000077000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_302"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0304',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007700000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_303"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0305',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000770000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_304"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0306',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000077000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_305"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0307',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007700000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_306"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0308',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000770000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_307"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0309',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000077000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_308"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0310',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007700000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_309"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0311',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000770000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_310"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0312',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000077000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_311"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0313',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007700000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_312"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0314',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000770000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_313"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0315',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000077000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_314"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0316',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007700000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_315"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0317',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000770000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_316"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0318',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000077000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_317"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0319',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007700000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_318"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0320',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000770000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_319"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0321',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000077000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_320"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0322',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007700000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_321"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0323',
                sections = [
                    Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100180400000000800000770000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_322"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0324',
                sections = [
                    Section.Code(code=Op.PUSH24[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000017700000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_323"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0325',
                sections = [
                    Section.Code(code=[0x78], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000078",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_324"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0326',
                sections = [
                    Section.Code(code=[0x78, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007800",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_325"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0327',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000780000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_326"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0328',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000078000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_327"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0329',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007800000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_328"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0330',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000780000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_329"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0331',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000078000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_330"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0332',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007800000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_331"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0333',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000780000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_332"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0334',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000078000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_333"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0335',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007800000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_334"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0336',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000780000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_335"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0337',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000078000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_336"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0338',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007800000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_337"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0339',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000780000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_338"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0340',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000078000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_339"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0341',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007800000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_340"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0342',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000780000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_341"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0343',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000078000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_342"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0344',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007800000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_343"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0345',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000780000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_344"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0346',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000078000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_345"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0347',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007800000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_346"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0348',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100180400000000800000780000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_347"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0349',
                sections = [
                    Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010019040000000080000078000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_348"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0350',
                sections = [
                    Section.Code(code=Op.PUSH25[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001b0400000000800001780000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_349"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0351',
                sections = [
                    Section.Code(code=[0x79], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010001040000000080000079",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_350"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0352',
                sections = [
                    Section.Code(code=[0x79, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007900",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_351"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0353',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100030400000000800000790000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_352"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0354',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010004040000000080000079000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_353"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0355',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007900000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_354"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0356',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100060400000000800000790000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_355"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0357',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010007040000000080000079000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_356"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0358',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007900000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_357"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0359',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100090400000000800000790000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_358"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0360',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a040000000080000079000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_359"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0361',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007900000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_360"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0362',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c0400000000800000790000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_361"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0363',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d040000000080000079000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_362"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0364',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007900000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_363"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0365',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f0400000000800000790000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_364"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0366',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010010040000000080000079000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_365"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0367',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007900000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_366"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0368',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100120400000000800000790000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_367"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0369',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010013040000000080000079000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_368"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0370',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007900000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_369"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0371',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100150400000000800000790000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_370"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0372',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010016040000000080000079000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_371"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0373',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007900000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_372"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0374',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef000101000402000100180400000000800000790000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_373"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0375',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef00010100040200010019040000000080000079000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_374"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0376',
                sections = [
                    Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007900000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_375"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0377',
                sections = [
                    Section.Code(code=Op.PUSH26[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001c040000000080000179000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_376"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0378',
                sections = [
                    Section.Code(code=[0x7a], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007a",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_377"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0379',
                sections = [
                    Section.Code(code=[0x7a, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007a00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_378"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0380',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007a0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_379"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0381',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007a000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_380"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0382',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007a00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_381"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0383',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007a0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_382"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0384',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007a000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_383"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0385',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007a00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_384"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0386',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007a0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_385"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0387',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007a000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_386"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0388',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007a00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_387"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0389',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007a0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_388"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0390',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007a000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_389"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0391',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007a00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_390"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0392',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007a0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_391"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0393',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007a000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_392"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0394',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007a00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_393"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0395',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007a0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_394"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0396',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007a000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_395"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0397',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007a00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_396"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0398',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007a0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_397"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0399',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007a000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_398"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0400',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007a00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_399"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0401',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007a0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_400"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0402',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007a000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_401"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0403',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007a00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_402"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0404',
                sections = [
                    Section.Code(code=[0x7a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007a0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_403"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0405',
                sections = [
                    Section.Code(code=Op.PUSH27[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001d04000000008000017a00000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_404"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0406',
                sections = [
                    Section.Code(code=[0x7b], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007b",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_405"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0407',
                sections = [
                    Section.Code(code=[0x7b, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007b00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_406"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0408',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007b0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_407"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0409',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007b000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_408"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0410',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007b00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_409"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0411',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007b0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_410"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0412',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007b000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_411"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0413',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007b00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_412"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0414',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007b0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_413"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0415',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007b000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_414"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0416',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007b00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_415"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0417',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007b0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_416"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0418',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007b000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_417"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0419',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007b00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_418"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0420',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007b0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_419"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0421',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007b000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_420"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0422',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007b00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_421"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0423',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007b0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_422"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0424',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007b000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_423"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0425',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007b00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_424"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0426',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007b0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_425"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0427',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007b000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_426"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0428',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007b00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_427"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0429',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007b0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_428"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0430',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007b000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_429"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0431',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007b00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_430"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0432',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007b0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_431"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0433',
                sections = [
                    Section.Code(code=[0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001c04000000008000007b000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_432"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0434',
                sections = [
                    Section.Code(code=Op.PUSH28[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001e04000000008000017b0000000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_433"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0435',
                sections = [
                    Section.Code(code=[0x7c], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007c",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_434"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0436',
                sections = [
                    Section.Code(code=[0x7c, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007c00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_435"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0437',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007c0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_436"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0438',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007c000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_437"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0439',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007c00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_438"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0440',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007c0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_439"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0441',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007c000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_440"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0442',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007c00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_441"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0443',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007c0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_442"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0444',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007c000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_443"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0445',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007c00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_444"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0446',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007c0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_445"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0447',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007c000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_446"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0448',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007c00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_447"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0449',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007c0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_448"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0450',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007c000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_449"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0451',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007c00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_450"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0452',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007c0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_451"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0453',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007c000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_452"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0454',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007c00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_453"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0455',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007c0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_454"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0456',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007c000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_455"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0457',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007c00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_456"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0458',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007c0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_457"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0459',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007c000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_458"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0460',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007c00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_459"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0461',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007c0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_460"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0462',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001c04000000008000007c000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_461"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0463',
                sections = [
                    Section.Code(code=[0x7c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001d04000000008000007c00000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_462"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0464',
                sections = [
                    Section.Code(code=Op.PUSH29[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001001f04000000008000017c000000000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_463"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0465',
                sections = [
                    Section.Code(code=[0x7d], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007d",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_464"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0466',
                sections = [
                    Section.Code(code=[0x7d, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007d00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_465"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0467',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007d0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_466"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0468',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007d000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_467"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0469',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007d00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_468"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0470',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007d0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_469"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0471',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007d000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_470"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0472',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007d00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_471"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0473',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007d0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_472"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0474',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007d000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_473"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0475',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007d00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_474"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0476',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007d0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_475"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0477',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007d000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_476"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0478',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007d00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_477"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0479',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007d0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_478"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0480',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007d000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_479"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0481',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007d00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_480"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0482',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007d0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_481"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0483',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007d000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_482"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0484',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007d00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_483"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0485',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007d0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_484"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0486',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007d000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_485"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0487',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007d00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_486"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0488',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007d0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_487"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0489',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007d000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_488"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0490',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007d00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_489"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0491',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007d0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_490"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0492',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001c04000000008000007d000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_491"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0493',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001d04000000008000007d00000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_492"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0494',
                sections = [
                    Section.Code(code=[0x7d, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001e04000000008000007d0000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_493"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0495',
                sections = [
                    Section.Code(code=Op.PUSH30[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001002004000000008000017d00000000000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_494"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0496',
                sections = [
                    Section.Code(code=[0x7e], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007e",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_495"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0497',
                sections = [
                    Section.Code(code=[0x7e, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007e00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_496"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0498',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007e0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_497"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0499',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007e000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_498"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0500',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007e00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_499"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0501',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007e0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_500"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0502',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007e000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_501"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0503',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007e00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_502"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0504',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007e0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_503"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0505',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007e000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_504"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0506',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007e00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_505"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0507',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007e0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_506"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0508',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007e000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_507"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0509',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007e00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_508"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0510',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007e0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_509"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0511',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007e000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_510"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0512',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007e00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_511"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0513',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007e0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_512"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0514',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007e000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_513"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0515',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007e00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_514"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0516',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007e0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_515"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0517',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007e000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_516"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0518',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007e00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_517"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0519',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007e0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_518"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0520',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007e000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_519"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0521',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007e00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_520"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0522',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007e0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_521"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0523',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001c04000000008000007e000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_522"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0524',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001d04000000008000007e00000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_523"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0525',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001e04000000008000007e0000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_524"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0526',
                sections = [
                    Section.Code(code=[0x7e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001f04000000008000007e000000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_525"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0527',
                sections = [
                    Section.Code(code=Op.PUSH31[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001002104000000008000017e0000000000000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_526"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0528',
                sections = [
                    Section.Code(code=[0x7f], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000104000000008000007f",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_527"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0529',
                sections = [
                    Section.Code(code=[0x7f, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000204000000008000007f00",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_528"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0530',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000304000000008000007f0000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_529"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0531',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000404000000008000007f000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_530"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0532',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000504000000008000007f00000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_531"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0533',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000604000000008000007f0000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_532"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0534',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000704000000008000007f000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_533"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0535',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000804000000008000007f00000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_534"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0536',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000904000000008000007f0000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_535"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0537',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000a04000000008000007f000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_536"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0538',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000b04000000008000007f00000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_537"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0539',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000c04000000008000007f0000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_538"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0540',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000d04000000008000007f000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_539"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0541',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000e04000000008000007f00000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_540"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0542',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001000f04000000008000007f0000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_541"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0543',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001004000000008000007f000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_542"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0544',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001104000000008000007f00000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_543"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0545',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001204000000008000007f0000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_544"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0546',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001304000000008000007f000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_545"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0547',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001404000000008000007f00000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_546"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0548',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001504000000008000007f0000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_547"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0549',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001604000000008000007f000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_548"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0550',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001704000000008000007f00000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_549"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0551',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001804000000008000007f0000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_550"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0552',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001904000000008000007f000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_551"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0553',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001a04000000008000007f00000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_552"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0554',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001b04000000008000007f0000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_553"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0555',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001c04000000008000007f000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_554"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0556',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001d04000000008000007f00000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_555"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0557',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001e04000000008000007f0000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_556"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0558',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001001f04000000008000007f000000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_557"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0559',
                sections = [
                    Section.Code(code=[0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], max_stack_height=0),
                    ],
              )
              ,
              "ef0001010004020001002004000000008000007f00000000000000000000000000000000000000000000000000000000000000",
              EOFException.TRUNCATED_INSTRUCTION,
              id="eof1_truncated_push_558"
        ),
        pytest.param(
              Container(
                name = 'EOFV1_0560',
                sections = [
                    Section.Code(code=Op.PUSH32[0] + Op.STOP, max_stack_height=1),
                    ],
              )
              ,
              "ef0001010004020001002204000000008000017f000000000000000000000000000000000000000000000000000000000000000000",
              None,
              id="eof1_truncated_push_559"
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
