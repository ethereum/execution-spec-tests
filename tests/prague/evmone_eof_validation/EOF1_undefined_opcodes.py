"""
EOF v1 validation code
"""

import pytest
from ethereum_test_tools import EOFTestFiller
from ethereum_test_tools import EOFException, Opcodes as Op, UndefinedOpcodes as UOp
from ethereum_test_tools.eof.v1 import Container, ContainerKind, Section

@pytest.mark.parametrize(
    "eof_code,expected_hex_bytecode,exception",
    [
        
        pytest.param(
                Container(
                    name="EOF1V00001",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef00010100040200010013040000000080001160018080808080808080808080808080808000",
                None,
                id="valid_opcode_STOP",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00002",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.ADD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800100",
                None,
                id="valid_opcode_ADD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00003",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MUL + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800200",
                None,
                id="valid_opcode_MUL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00004",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SUB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800300",
                None,
                id="valid_opcode_SUB",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00005",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DIV + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800400",
                None,
                id="valid_opcode_DIV",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00006",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SDIV + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800500",
                None,
                id="valid_opcode_SDIV",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00007",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MOD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800600",
                None,
                id="valid_opcode_MOD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00008",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SMOD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800700",
                None,
                id="valid_opcode_SMOD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00009",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.ADDMOD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800800",
                None,
                id="valid_opcode_ADDMOD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00010",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MULMOD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800900",
                None,
                id="valid_opcode_MULMOD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00011",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.EXP + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800a00",
                None,
                id="valid_opcode_EXP",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00012",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SIGNEXTEND + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800b00",
                None,
                id="valid_opcode_SIGNEXTEND",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00013",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_0C + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800c00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00014",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_0D + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800d00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00015",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_0E + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800e00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xe",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00016",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_0F + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080800f00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00017",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LT + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801000",
                None,
                id="valid_opcode_LT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00018",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.GT + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801100",
                None,
                id="valid_opcode_GT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00019",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SLT + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801200",
                None,
                id="valid_opcode_SLT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00020",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SGT + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801300",
                None,
                id="valid_opcode_SGT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00021",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.EQ + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801400",
                None,
                id="valid_opcode_EQ",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00022",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.ISZERO + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801500",
                None,
                id="valid_opcode_ISZERO",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00023",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.AND + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801600",
                None,
                id="valid_opcode_AND",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00024",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.OR + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801700",
                None,
                id="valid_opcode_OR",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00025",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.XOR + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801800",
                None,
                id="valid_opcode_XOR",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00026",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.NOT + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801900",
                None,
                id="valid_opcode_NOT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00027",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BYTE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801a00",
                None,
                id="valid_opcode_BYTE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00028",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SHL + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801b00",
                None,
                id="valid_opcode_SHL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00029",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SHR + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801c00",
                None,
                id="valid_opcode_SHR",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00030",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SAR + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801d00",
                None,
                id="valid_opcode_SAR",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00031",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_1E + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801e00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x1e",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00032",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_1F + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080801f00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x1f",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00033",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SHA3 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802000",
                None,
                id="valid_opcode_KECCAK256",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00034",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_21 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802100",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x21",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00035",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_22 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802200",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x22",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00036",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_23 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802300",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x23",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00037",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_24 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802400",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x24",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00038",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_25 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802500",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x25",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00039",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_26 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x26",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00040",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_27 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802700",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x27",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00041",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_28 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802800",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x28",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00042",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_29 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x29",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00043",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2A + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802a00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2a",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00044",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2B + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802b00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00045",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2C + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802c00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2c",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00046",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2D + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802d00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2d",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00047",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2E + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802e00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2e",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00048",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_2F + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080802f00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x2f",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00049",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.ADDRESS + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803000",
                None,
                id="valid_opcode_ADDRESS",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00050",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BALANCE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080803100",
                None,
                id="valid_opcode_BALANCE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00051",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.ORIGIN + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803200",
                None,
                id="valid_opcode_ORIGIN",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00052",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CALLER + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803300",
                None,
                id="valid_opcode_CALLER",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00053",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CALLVALUE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803400",
                None,
                id="valid_opcode_CALLVALUE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00054",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CALLDATALOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080803500",
                None,
                id="valid_opcode_CALLDATALOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00055",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CALLDATASIZE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803600",
                None,
                id="valid_opcode_CALLDATASIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00056",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CALLDATACOPY + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080803700",
                None,
                id="valid_opcode_CALLDATACOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00057",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.GASPRICE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803a00",
                None,
                id="valid_opcode_GASPRICE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00058",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.RETURNDATASIZE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080803d00",
                None,
                id="valid_opcode_RETURNDATASIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00059",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.RETURNDATACOPY + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080803e00",
                None,
                id="valid_opcode_RETURNDATACOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00060",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BLOCKHASH + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804000",
                None,
                id="valid_opcode_BLOCKHASH",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00061",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.COINBASE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804100",
                None,
                id="valid_opcode_COINBASE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00062",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.TIMESTAMP + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804200",
                None,
                id="valid_opcode_TIMESTAMP",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00063",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.NUMBER + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804300",
                None,
                id="valid_opcode_NUMBER",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00064",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.PREVRANDAO + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804400",
                None,
                id="valid_opcode_PREVRANDAO",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00065",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.GASLIMIT + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804500",
                None,
                id="valid_opcode_GASLIMIT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00066",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.CHAINID + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804600",
                None,
                id="valid_opcode_CHAINID",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00067",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SELFBALANCE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804700",
                None,
                id="valid_opcode_SELFBALANCE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00068",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BASEFEE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804800",
                None,
                id="valid_opcode_BASEFEE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00069",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BLOBHASH + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804900",
                None,
                id="valid_opcode_BLOBHASH",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00070",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.BLOBBASEFEE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080804a00",
                None,
                id="valid_opcode_BLOBBASEFEE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00071",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_4B + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804b00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x4b",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00072",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_4C + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804c00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x4c",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00073",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_4D + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804d00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x4d",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00074",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_4E + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804e00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x4e",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00075",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_4F + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080804f00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0x4f",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00076",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.POP + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805000",
                None,
                id="valid_opcode_POP",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00077",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MLOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805100",
                None,
                id="valid_opcode_MLOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00078",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MSTORE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805200",
                None,
                id="valid_opcode_MSTORE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00079",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MSTORE8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805300",
                None,
                id="valid_opcode_MSTORE8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00080",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SLOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805400",
                None,
                id="valid_opcode_SLOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00081",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SSTORE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805500",
                None,
                id="valid_opcode_SSTORE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00082",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MSIZE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080805900",
                None,
                id="valid_opcode_MSIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00083",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.JUMPDEST + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805b00",
                None,
                id="valid_opcode_JUMPDEST",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00084",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.TLOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805c00",
                None,
                id="valid_opcode_TLOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00085",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.TSTORE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805d00",
                None,
                id="valid_opcode_TSTORE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00086",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.MCOPY + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080805e00",
                None,
                id="valid_opcode_MCOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00087",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.PUSH0 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080805f00",
                None,
                id="valid_opcode_PUSH0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00088",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 17 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808000",
                None,
                id="valid_opcode_DUP1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00089",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP2 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808100",
                None,
                id="valid_opcode_DUP2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00090",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP3 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808200",
                None,
                id="valid_opcode_DUP3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00091",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP4 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808300",
                None,
                id="valid_opcode_DUP4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00092",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP5 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808400",
                None,
                id="valid_opcode_DUP5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00093",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP6 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808500",
                None,
                id="valid_opcode_DUP6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00094",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP7 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808600",
                None,
                id="valid_opcode_DUP7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00095",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP8 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808700",
                None,
                id="valid_opcode_DUP8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00096",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP9 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808800",
                None,
                id="valid_opcode_DUP9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00097",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP10 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808900",
                None,
                id="valid_opcode_DUP10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00098",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP11 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808a00",
                None,
                id="valid_opcode_DUP11",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00099",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP12 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808b00",
                None,
                id="valid_opcode_DUP12",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00100",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP13 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808c00",
                None,
                id="valid_opcode_DUP13",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00101",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP14 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808d00",
                None,
                id="valid_opcode_DUP14",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00102",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP15 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808e00",
                None,
                id="valid_opcode_DUP15",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00103",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DUP16 + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000126001808080808080808080808080808080808f00",
                None,
                id="valid_opcode_DUP16",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00104",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP1 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809000",
                None,
                id="valid_opcode_SWAP1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00105",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP2 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809100",
                None,
                id="valid_opcode_SWAP2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00106",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP3 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809200",
                None,
                id="valid_opcode_SWAP3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00107",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP4 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809300",
                None,
                id="valid_opcode_SWAP4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00108",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP5 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809400",
                None,
                id="valid_opcode_SWAP5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00109",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809500",
                None,
                id="valid_opcode_SWAP6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00110",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP7 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809600",
                None,
                id="valid_opcode_SWAP7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00111",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809700",
                None,
                id="valid_opcode_SWAP8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00112",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809800",
                None,
                id="valid_opcode_SWAP9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00113",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP10 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809900",
                None,
                id="valid_opcode_SWAP10",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00114",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP11 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809a00",
                None,
                id="valid_opcode_SWAP11",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00115",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP12 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809b00",
                None,
                id="valid_opcode_SWAP12",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00116",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP13 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809c00",
                None,
                id="valid_opcode_SWAP13",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00117",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP14 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809d00",
                None,
                id="valid_opcode_SWAP14",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00118",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP15 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809e00",
                None,
                id="valid_opcode_SWAP15",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00119",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.SWAP16 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef0001010004020001001404000000008000116001808080808080808080808080808080809f00",
                None,
                id="valid_opcode_SWAP16",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00120",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LOG0 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a000",
                None,
                id="valid_opcode_LOG0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00121",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LOG1 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a100",
                None,
                id="valid_opcode_LOG1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00122",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LOG2 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a200",
                None,
                id="valid_opcode_LOG2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00123",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LOG3 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a300",
                None,
                id="valid_opcode_LOG3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00124",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.LOG4 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a400",
                None,
                id="valid_opcode_LOG4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00125",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_A5 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a500",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xa5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00126",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_A6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xa6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00127",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_A7 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a700",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xa7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00128",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_A8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a800",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xa8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00129",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_A9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080a900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xa9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00130",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AA + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080aa00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xaa",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00131",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ab00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xab",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00132",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AC + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ac00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xac",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00133",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ad00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xad",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00134",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ae00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xae",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00135",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_AF + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080af00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xaf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00136",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B0 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b000",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00137",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B1 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b100",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00138",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B2 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b200",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00139",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B3 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b300",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00140",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B4 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b400",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00141",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B5 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b500",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00142",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00143",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B7 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b700",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00144",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b800",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00145",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_B9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080b900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xb9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00146",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BA + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ba00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xba",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00147",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080bb00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xbb",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00148",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BC + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080bc00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xbc",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00149",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080bd00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xbd",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00150",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080be00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xbe",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00151",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_BF + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080bf00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xbf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00152",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C0 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c000",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc0",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00153",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C1 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c100",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc1",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00154",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C2 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c200",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc2",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00155",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C3 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c300",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc3",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00156",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C4 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c400",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00157",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C5 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c500",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00158",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00159",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C7 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c700",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00160",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c800",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00161",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_C9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080c900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xc9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00162",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CA + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ca00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xca",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00163",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080cb00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xcb",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00164",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CC + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080cc00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xcc",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00165",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080cd00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xcd",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00166",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ce00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xce",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00167",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_CF + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080cf00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xcf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00168",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DATALOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d000",
                None,
                id="valid_opcode_DATALOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00169",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DATASIZE + Op.STOP, max_stack_height=18),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800012600180808080808080808080808080808080d200",
                None,
                id="valid_opcode_DATASIZE",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00170",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.DATACOPY + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d300",
                None,
                id="valid_opcode_DATACOPY",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00171",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D4 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d400",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd4",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00172",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D5 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d500",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd5",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00173",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00174",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D7 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d700",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd7",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00175",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D8 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d800",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd8",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00176",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_D9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080d900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xd9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00177",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DA + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080da00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xda",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00178",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080db00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xdb",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00179",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DC + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080dc00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xdc",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00180",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080dd00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xdd",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00181",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DE + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080de00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xde",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00182",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_DF + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080df00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xdf",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00183",
                    sections=[
                        Section.Code(code=Op.CALLF[0x0001] + Op.STOP, max_stack_height=0),
						Section.Code(code=Op.RETF, code_outputs=0, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000802000200040001040000000080000000000000e3000100e4",
                None,
                id="valid_opcode_RETF",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00184",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_E9 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080e900",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xe9",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00185",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_EA + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ea00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xea",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00186",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_EB + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080eb00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xeb",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00187",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_ED + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ed00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xed",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00188",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_EF + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080ef00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xef",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00189",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.RETURN, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100130400000000800011600180808080808080808080808080808080f3",
                None,
                id="valid_opcode_RETURN",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00190",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_F6 + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080f600",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xf6",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00191",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.RETURNDATALOAD + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080f700",
                None,
                id="valid_opcode_RETURNDATALOAD",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00192",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.EXTCALL + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080f800",
                None,
                id="valid_opcode_EXTCALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00193",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.EXTDELEGATECALL + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080f900",
                None,
                id="valid_opcode_EXTDELEGATECALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00194",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.EXTSTATICCALL + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080fb00",
                None,
                id="valid_opcode_EXTSTATICCALL",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00195",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + UOp.OPCODE_FC + Op.STOP, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100140400000000800011600180808080808080808080808080808080fc00",
                EOFException.UNDEFINED_INSTRUCTION,
                id="undefined_instruction_0xfc",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00196",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.REVERT, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100130400000000800011600180808080808080808080808080808080fd",
                None,
                id="valid_opcode_REVERT",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00197",
                    sections=[
                        Section.Code(code=Op.PUSH1[0x01] + Op.DUP1 * 16 + Op.INVALID, max_stack_height=17),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100130400000000800011600180808080808080808080808080808080fe",
                None,
                id="valid_opcode_INVALID",
            ),
                
        pytest.param(
                Container(
                    name="EOF1V00198",
                    sections=[
                        Section.Code(code=Op.INVALID, max_stack_height=0),
                    ],
                    kind=ContainerKind.RUNTIME,
                ),
                "0xef000101000402000100010400000000800000fe",
                None,
                id="EOF1_undefined_opcodes_198",
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
    if expected_hex_bytecode[0:2] == "0x":
        expected_hex_bytecode = expected_hex_bytecode[2:]
    assert bytes(eof_code) == bytes.fromhex(expected_hex_bytecode)

    eof_test(
        data=eof_code,
        expect_exception=exception,
    )
