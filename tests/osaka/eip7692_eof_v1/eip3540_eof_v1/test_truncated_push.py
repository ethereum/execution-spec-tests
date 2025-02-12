"""EOF v1 validation code - Exported from evmone unit tests."""

import pytest
from ethereum_test_tools import EOFTestFiller, EOFException, Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, Section

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="truncated_push_instruction_0",
            sections=[
                Section.Code(code=[0x60],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000060",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_1",
            sections=[
                Section.Code(code=Op.PUSH1[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef000101000402000100030400000000800001600000",
          ),
        Container(
            name="truncated_push_instruction_2",
            sections=[
                Section.Code(code=[0x61],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000061",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_3",
            sections=[
                Section.Code(code=[0x61, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006100",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_4",
            sections=[
                Section.Code(code=Op.PUSH2[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef00010100040200010004040000000080000161000000",
          ),
        Container(
            name="truncated_push_instruction_5",
            sections=[
                Section.Code(code=[0x62],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000062",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_6",
            sections=[
                Section.Code(code=[0x62, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006200",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_7",
            sections=[
                Section.Code(code=[0x62, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000620000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_8",
            sections=[
                Section.Code(code=Op.PUSH3[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000504000000008000016200000000",
          ),
        Container(
            name="truncated_push_instruction_9",
            sections=[
                Section.Code(code=[0x63],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000063",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_10",
            sections=[
                Section.Code(code=[0x63, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006300",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_11",
            sections=[
                Section.Code(code=[0x63, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000630000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_12",
            sections=[
                Section.Code(code=[0x63, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000063000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_13",
            sections=[
                Section.Code(code=Op.PUSH4[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef000101000402000100060400000000800001630000000000",
          ),
        Container(
            name="truncated_push_instruction_14",
            sections=[
                Section.Code(code=[0x64],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000064",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_15",
            sections=[
                Section.Code(code=[0x64, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006400",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_16",
            sections=[
                Section.Code(code=[0x64, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000640000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_17",
            sections=[
                Section.Code(code=[0x64, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000064000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_18",
            sections=[
                Section.Code(code=[0x64, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006400000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_19",
            sections=[
                Section.Code(code=Op.PUSH5[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef00010100040200010007040000000080000164000000000000",
          ),
        Container(
            name="truncated_push_instruction_20",
            sections=[
                Section.Code(code=[0x65],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000065",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_21",
            sections=[
                Section.Code(code=[0x65, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006500",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_22",
            sections=[
                Section.Code(code=[0x65, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000650000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_23",
            sections=[
                Section.Code(code=[0x65, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000065000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_24",
            sections=[
                Section.Code(code=[0x65, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006500000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_25",
            sections=[
                Section.Code(code=[0x65, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000650000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_26",
            sections=[
                Section.Code(code=Op.PUSH6[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000804000000008000016500000000000000",
          ),
        Container(
            name="truncated_push_instruction_27",
            sections=[
                Section.Code(code=[0x66],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000066",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_28",
            sections=[
                Section.Code(code=[0x66, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006600",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_29",
            sections=[
                Section.Code(code=[0x66, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000660000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_30",
            sections=[
                Section.Code(code=[0x66, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000066000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_31",
            sections=[
                Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006600000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_32",
            sections=[
                Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000660000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_33",
            sections=[
                Section.Code(code=[0x66, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000066000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_34",
            sections=[
                Section.Code(code=Op.PUSH7[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef000101000402000100090400000000800001660000000000000000",
          ),
        Container(
            name="truncated_push_instruction_35",
            sections=[
                Section.Code(code=[0x67],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000067",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_36",
            sections=[
                Section.Code(code=[0x67, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006700",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_37",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000670000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_38",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000067000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_39",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006700000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_40",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000670000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_41",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000067000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_42",
            sections=[
                Section.Code(code=[0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006700000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_43",
            sections=[
                Section.Code(code=Op.PUSH8[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000167000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_44",
            sections=[
                Section.Code(code=[0x68],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000068",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_45",
            sections=[
                Section.Code(code=[0x68, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006800",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_46",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000680000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_47",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000068000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_48",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006800000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_49",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000680000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_50",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000068000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_51",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006800000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_52",
            sections=[
                Section.Code(code=[0x68, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000680000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_53",
            sections=[
                Section.Code(code=Op.PUSH9[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000016800000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_54",
            sections=[
                Section.Code(code=[0x69],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000069",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_55",
            sections=[
                Section.Code(code=[0x69, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006900",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_56",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000690000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_57",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000069000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_58",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006900000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_59",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000690000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_60",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000069000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_61",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006900000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_62",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000690000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_63",
            sections=[
                Section.Code(code=[0x69, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000069000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_64",
            sections=[
                Section.Code(code=Op.PUSH10[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800001690000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_65",
            sections=[
                Section.Code(code=[0x6A],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006a",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_66",
            sections=[
                Section.Code(code=[0x6A, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006a00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_67",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006a0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_68",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006a000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_69",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006a00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_70",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006a0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_71",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006a000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_72",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006a00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_73",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006a0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_74",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006a000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_75",
            sections=[
                Section.Code(code=[0x6A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006a00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_76",
            sections=[
                Section.Code(code=Op.PUSH11[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000016a000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_77",
            sections=[
                Section.Code(code=[0x6B],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006b",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_78",
            sections=[
                Section.Code(code=[0x6B, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006b00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_79",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006b0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_80",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006b000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_81",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006b00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_82",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006b0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_83",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006b000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_84",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006b00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_85",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006b0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_86",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006b000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_87",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006b00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_88",
            sections=[
                Section.Code(code=[0x6B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000006b0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_89",
            sections=[
                Section.Code(code=Op.PUSH12[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000016b00000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_90",
            sections=[
                Section.Code(code=[0x6C],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006c",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_91",
            sections=[
                Section.Code(code=[0x6C, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006c00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_92",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006c0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_93",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006c000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_94",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006c00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_95",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006c0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_96",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006c000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_97",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006c00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_98",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006c0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_99",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006c000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_100",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006c00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_101",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000006c0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_102",
            sections=[
                Section.Code(code=[0x6C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000006c000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_103",
            sections=[
                Section.Code(code=Op.PUSH13[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000016c0000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_104",
            sections=[
                Section.Code(code=[0x6D],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006d",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_105",
            sections=[
                Section.Code(code=[0x6D, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006d00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_106",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006d0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_107",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006d000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_108",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006d00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_109",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006d0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_110",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006d000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_111",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006d00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_112",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006d0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_113",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006d000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_114",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006d00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_115",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000006d0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_116",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000006d000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_117",
            sections=[
                Section.Code(code=[0x6D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000006d00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_118",
            sections=[
                Section.Code(code=Op.PUSH14[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001004000000008000016d000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_119",
            sections=[
                Section.Code(code=[0x6E],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006e",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_120",
            sections=[
                Section.Code(code=[0x6E, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006e00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_121",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006e0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_122",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006e000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_123",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006e00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_124",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006e0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_125",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006e000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_126",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006e00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_127",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006e0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_128",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006e000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_129",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006e00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_130",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000006e0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_131",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000006e000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_132",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000006e00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_133",
            sections=[
                Section.Code(code=[0x6E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000006e0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_134",
            sections=[
                Section.Code(code=Op.PUSH15[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001104000000008000016e00000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_135",
            sections=[
                Section.Code(code=[0x6F],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000006f",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_136",
            sections=[
                Section.Code(code=[0x6F, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000006f00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_137",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000006f0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_138",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000006f000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_139",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000006f00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_140",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000006f0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_141",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000006f000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_142",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000006f00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_143",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000006f0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_144",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000006f000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_145",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000006f00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_146",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000006f0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_147",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000006f000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_148",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000006f00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_149",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000006f0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_150",
            sections=[
                Section.Code(code=[0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000006f000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_151",
            sections=[
                Section.Code(code=Op.PUSH16[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001204000000008000016f0000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_152",
            sections=[
                Section.Code(code=[0x70],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000070",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_153",
            sections=[
                Section.Code(code=[0x70, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_154",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000700000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_155",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000070000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_156",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_157",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000700000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_158",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000070000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_159",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_160",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000700000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_161",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000070000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_162",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_163",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000700000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_164",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000070000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_165",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_166",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000700000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_167",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000070000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_168",
            sections=[
                Section.Code(code=[0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_169",
            sections=[
                Section.Code(code=Op.PUSH17[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef00010100040200010013040000000080000170000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_170",
            sections=[
                Section.Code(code=[0x71],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000071",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_171",
            sections=[
                Section.Code(code=[0x71, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007100",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_172",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000710000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_173",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000071000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_174",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007100000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_175",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000710000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_176",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000071000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_177",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007100000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_178",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000710000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_179",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000071000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_180",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007100000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_181",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000710000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_182",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000071000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_183",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007100000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_184",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000710000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_185",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000071000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_186",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007100000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_187",
            sections=[
                Section.Code(code=[0x71, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000710000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_188",
            sections=[
                Section.Code(code=Op.PUSH18[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001404000000008000017100000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_189",
            sections=[
                Section.Code(code=[0x72],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000072",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_190",
            sections=[
                Section.Code(code=[0x72, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007200",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_191",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000720000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_192",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000072000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_193",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007200000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_194",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000720000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_195",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000072000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_196",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007200000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_197",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000720000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_198",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000072000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_199",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007200000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_200",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000720000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_201",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000072000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_202",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007200000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_203",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000720000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_204",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000072000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_205",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007200000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_206",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000720000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_207",
            sections=[
                Section.Code(code=[0x72, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000072000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_208",
            sections=[
                Section.Code(code=Op.PUSH19[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef000101000402000100150400000000800001720000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_209",
            sections=[
                Section.Code(code=[0x73],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000073",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_210",
            sections=[
                Section.Code(code=[0x73, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007300",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_211",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000730000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_212",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000073000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_213",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007300000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_214",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000730000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_215",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000073000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_216",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007300000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_217",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000730000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_218",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000073000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_219",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007300000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_220",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000730000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_221",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000073000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_222",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007300000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_223",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000730000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_224",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000073000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_225",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007300000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_226",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000730000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_227",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000073000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_228",
            sections=[
                Section.Code(code=[0x73, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007300000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_229",
            sections=[
                Section.Code(code=Op.PUSH20[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef00010100040200010016040000000080000173000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_230",
            sections=[
                Section.Code(code=[0x74],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000074",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_231",
            sections=[
                Section.Code(code=[0x74, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007400",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_232",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000740000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_233",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000074000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_234",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007400000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_235",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000740000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_236",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000074000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_237",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007400000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_238",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000740000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_239",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000074000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_240",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007400000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_241",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000740000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_242",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000074000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_243",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007400000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_244",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000740000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_245",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000074000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_246",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007400000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_247",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000740000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_248",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000074000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_249",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007400000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_250",
            sections=[
                Section.Code(code=[0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000740000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_251",
            sections=[
                Section.Code(code=Op.PUSH21[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001704000000008000017400000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_252",
            sections=[
                Section.Code(code=[0x75],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000075",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_253",
            sections=[
                Section.Code(code=[0x75, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007500",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_254",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000750000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_255",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000075000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_256",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007500000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_257",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000750000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_258",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000075000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_259",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007500000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_260",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000750000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_261",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000075000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_262",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007500000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_263",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000750000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_264",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000075000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_265",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007500000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_266",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000750000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_267",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000075000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_268",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007500000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_269",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000750000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_270",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000075000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_271",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007500000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_272",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000750000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_273",
            sections=[
                Section.Code(code=[0x75, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010016040000000080000075000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_274",
            sections=[
                Section.Code(code=Op.PUSH22[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef000101000402000100180400000000800001750000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_275",
            sections=[
                Section.Code(code=[0x76],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000076",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_276",
            sections=[
                Section.Code(code=[0x76, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007600",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_277",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000760000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_278",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000076000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_279",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007600000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_280",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000760000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_281",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000076000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_282",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007600000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_283",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000760000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_284",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000076000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_285",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007600000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_286",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000760000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_287",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000076000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_288",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007600000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_289",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000760000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_290",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000076000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_291",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007600000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_292",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000760000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_293",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000076000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_294",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007600000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_295",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000760000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_296",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010016040000000080000076000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_297",
            sections=[
                Section.Code(code=[0x76, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007600000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_298",
            sections=[
                Section.Code(code=Op.PUSH23[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef00010100040200010019040000000080000176000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_299",
            sections=[
                Section.Code(code=[0x77],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000077",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_300",
            sections=[
                Section.Code(code=[0x77, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007700",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_301",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000770000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_302",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000077000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_303",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007700000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_304",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000770000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_305",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000077000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_306",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007700000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_307",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000770000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_308",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000077000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_309",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007700000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_310",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000770000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_311",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000077000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_312",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007700000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_313",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000770000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_314",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000077000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_315",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007700000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_316",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000770000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_317",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000077000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_318",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007700000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_319",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000770000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_320",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010016040000000080000077000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_321",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007700000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_322",
            sections=[
                Section.Code(code=[0x77, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100180400000000800000770000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_323",
            sections=[
                Section.Code(code=Op.PUSH24[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000017700000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_324",
            sections=[
                Section.Code(code=[0x78],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000078",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_325",
            sections=[
                Section.Code(code=[0x78, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007800",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_326",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000780000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_327",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000078000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_328",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007800000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_329",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000780000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_330",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000078000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_331",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007800000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_332",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000780000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_333",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000078000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_334",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007800000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_335",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000780000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_336",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000078000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_337",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007800000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_338",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000780000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_339",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000078000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_340",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007800000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_341",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000780000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_342",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000078000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_343",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007800000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_344",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000780000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_345",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010016040000000080000078000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_346",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007800000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_347",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100180400000000800000780000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_348",
            sections=[
                Section.Code(code=[0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010019040000000080000078000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_349",
            sections=[
                Section.Code(code=Op.PUSH25[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001b0400000000800001780000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_350",
            sections=[
                Section.Code(code=[0x79],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010001040000000080000079",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_351",
            sections=[
                Section.Code(code=[0x79, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007900",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_352",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100030400000000800000790000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_353",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010004040000000080000079000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_354",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007900000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_355",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100060400000000800000790000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_356",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010007040000000080000079000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_357",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007900000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_358",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100090400000000800000790000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_359",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a040000000080000079000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_360",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007900000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_361",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c0400000000800000790000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_362",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d040000000080000079000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_363",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007900000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_364",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f0400000000800000790000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_365",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010010040000000080000079000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_366",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007900000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_367",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100120400000000800000790000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_368",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010013040000000080000079000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_369",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007900000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_370",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100150400000000800000790000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_371",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010016040000000080000079000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_372",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007900000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_373",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef000101000402000100180400000000800000790000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_374",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef00010100040200010019040000000080000079000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_375",
            sections=[
                Section.Code(code=[0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007900000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_376",
            sections=[
                Section.Code(code=Op.PUSH26[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001c040000000080000179000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_377",
            sections=[
                Section.Code(code=[0x7A],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007a",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_378",
            sections=[
                Section.Code(code=[0x7A, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007a00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_379",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007a0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_380",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007a000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_381",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007a00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_382",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007a0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_383",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007a000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_384",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007a00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_385",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007a0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_386",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007a000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_387",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007a00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_388",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007a0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_389",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007a000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_390",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007a00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_391",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007a0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_392",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007a000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_393",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007a00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_394",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007a0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_395",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007a000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_396",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007a00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_397",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007a0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_398",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007a000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_399",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007a00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_400",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007a0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_401",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007a000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_402",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007a00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_403",
            sections=[
                Section.Code(code=[0x7A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007a0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_404",
            sections=[
                Section.Code(code=Op.PUSH27[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001d04000000008000017a00000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_405",
            sections=[
                Section.Code(code=[0x7B],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007b",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_406",
            sections=[
                Section.Code(code=[0x7B, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007b00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_407",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007b0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_408",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007b000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_409",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007b00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_410",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007b0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_411",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007b000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_412",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007b00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_413",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007b0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_414",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007b000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_415",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007b00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_416",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007b0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_417",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007b000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_418",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007b00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_419",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007b0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_420",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007b000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_421",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007b00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_422",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007b0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_423",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007b000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_424",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007b00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_425",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007b0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_426",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007b000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_427",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007b00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_428",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007b0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_429",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007b000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_430",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007b00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_431",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007b0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_432",
            sections=[
                Section.Code(code=[0x7B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001c04000000008000007b000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_433",
            sections=[
                Section.Code(code=Op.PUSH28[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001e04000000008000017b0000000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_434",
            sections=[
                Section.Code(code=[0x7C],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007c",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_435",
            sections=[
                Section.Code(code=[0x7C, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007c00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_436",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007c0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_437",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007c000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_438",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007c00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_439",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007c0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_440",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007c000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_441",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007c00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_442",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007c0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_443",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007c000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_444",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007c00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_445",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007c0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_446",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007c000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_447",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007c00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_448",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007c0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_449",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007c000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_450",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007c00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_451",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007c0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_452",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007c000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_453",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007c00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_454",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007c0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_455",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007c000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_456",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007c00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_457",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007c0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_458",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007c000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_459",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007c00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_460",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007c0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_461",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001c04000000008000007c000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_462",
            sections=[
                Section.Code(code=[0x7C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001d04000000008000007c00000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_463",
            sections=[
                Section.Code(code=Op.PUSH29[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001001f04000000008000017c000000000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_464",
            sections=[
                Section.Code(code=[0x7D],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007d",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_465",
            sections=[
                Section.Code(code=[0x7D, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007d00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_466",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007d0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_467",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007d000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_468",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007d00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_469",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007d0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_470",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007d000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_471",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007d00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_472",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007d0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_473",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007d000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_474",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007d00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_475",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007d0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_476",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007d000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_477",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007d00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_478",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007d0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_479",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007d000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_480",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007d00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_481",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007d0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_482",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007d000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_483",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007d00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_484",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007d0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_485",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007d000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_486",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007d00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_487",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007d0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_488",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007d000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_489",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007d00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_490",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007d0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_491",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001c04000000008000007d000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_492",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001d04000000008000007d00000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_493",
            sections=[
                Section.Code(code=[0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001e04000000008000007d0000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_494",
            sections=[
                Section.Code(code=Op.PUSH30[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001002004000000008000017d00000000000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_495",
            sections=[
                Section.Code(code=[0x7E],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007e",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_496",
            sections=[
                Section.Code(code=[0x7E, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007e00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_497",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007e0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_498",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007e000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_499",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007e00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_500",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007e0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_501",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007e000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_502",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007e00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_503",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007e0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_504",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007e000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_505",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007e00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_506",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007e0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_507",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007e000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_508",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007e00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_509",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007e0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_510",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007e000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_511",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007e00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_512",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007e0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_513",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007e000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_514",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007e00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_515",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007e0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_516",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007e000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_517",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007e00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_518",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007e0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_519",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007e000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_520",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007e00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_521",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007e0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_522",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001c04000000008000007e000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_523",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001d04000000008000007e00000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_524",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001e04000000008000007e0000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_525",
            sections=[
                Section.Code(code=[0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001f04000000008000007e000000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_526",
            sections=[
                Section.Code(code=Op.PUSH31[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001002104000000008000017e0000000000000000000000000000000000000000000000000000000000000000",
          ),
        Container(
            name="truncated_push_instruction_527",
            sections=[
                Section.Code(code=[0x7F],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000104000000008000007f",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_528",
            sections=[
                Section.Code(code=[0x7F, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000204000000008000007f00",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_529",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000304000000008000007f0000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_530",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000404000000008000007f000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_531",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000504000000008000007f00000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_532",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000604000000008000007f0000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_533",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000704000000008000007f000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_534",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000804000000008000007f00000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_535",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000904000000008000007f0000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_536",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000a04000000008000007f000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_537",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000b04000000008000007f00000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_538",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000c04000000008000007f0000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_539",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000d04000000008000007f000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_540",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000e04000000008000007f00000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_541",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001000f04000000008000007f0000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_542",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001004000000008000007f000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_543",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001104000000008000007f00000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_544",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001204000000008000007f0000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_545",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001304000000008000007f000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_546",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001404000000008000007f00000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_547",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001504000000008000007f0000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_548",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001604000000008000007f000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_549",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001704000000008000007f00000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_550",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001804000000008000007f0000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_551",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001904000000008000007f000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_552",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001a04000000008000007f00000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_553",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001b04000000008000007f0000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_554",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001c04000000008000007f000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_555",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001d04000000008000007f00000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_556",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                ],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001e04000000008000007f0000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_557",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001001f04000000008000007f000000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_558",
            sections=[
                Section.Code(code=[0x7F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00],
                    max_stack_height=0),
            ],
            expected_bytecode="ef0001010004020001002004000000008000007f00000000000000000000000000000000000000000000000000000000000000",
            validity_error=[
                EOFException.TRUNCATED_INSTRUCTION
            ],
          ),
        Container(
            name="truncated_push_instruction_559",
            sections=[
                Section.Code(code=Op.PUSH32[0] + Op.STOP,
                    max_stack_height=1),
            ],
            expected_bytecode="ef0001010004020001002204000000008000017f000000000000000000000000000000000000000000000000000000000000000000",
          ),

    ],
    ids = lambda c: c.name,
)
def test_truncated_push(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF contract containing truncated PUSH instructions."""
    eof_test(
        container=container,
        expect_exception=container.validity_error,
    )
