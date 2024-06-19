"""
EOF Container: check how every opcode behaves in the middle of the valid eof container code
"""

from enum import Enum

import pytest

from ethereum_test_tools import EOFTestFiller, Opcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools.eof.v1 import Container, EOFException, Section

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3540.md"
REFERENCE_SPEC_VERSION = "8dcb0a8c1c0102c87224308028632cc986a61183"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

# Invalid Opcodes will produce EOFException.UNDEFINED_INSTRUCTION when used in EOFContainer
invalid_eof_opcodes = {
    Op.CODESIZE._name_,
    Op.SELFDESTRUCT._name_,
    Op.CREATE2._name_,
    Op.CODECOPY._name_,
    Op.EXTCODESIZE._name_,
    Op.EXTCODECOPY._name_,
    Op.EXTCODEHASH._name_,
    Op.JUMP._name_,
    Op.JUMPI._name_,
    Op.PC._name_,
    Op.GAS._name_,
    Op.CREATE._name_,
    Op.CALL._name_,
    Op.CALLCODE._name_,
    Op.DELEGATECALL._name_,
    Op.STATICCALL._name_,
}

# Halting the execution opcodes will produce EOFException.UNREACHABLE_INSTRUCTIONS
# as the code won't reach the terminating instruction in original eof code
halting_opcodes = {
    Op.STOP._name_,
    Op.JUMPF._name_,
    Op.RETURNCONTRACT._name_,
    Op.RETURN._name_,
    Op.REVERT._name_,
    Op.INVALID._name_,
}

# Special eof opcodes that require [] operator
eof_opcodes = {
    Op.DATALOADN._name_,
    Op.RJUMPV._name_,
    Op.CALLF._name_,
    Op.RETF._name_,
    Op.JUMPF._name_,
    Op.EOFCREATE._name_,
    Op.RETURNCONTRACT._name_,
    Op.EXCHANGE._name_,
}


class UndefinedOp(Opcode, Enum):
    """
    Enum containing all unknown opcodes (88 at the moment).
    """

    OPCODE_0C = Opcode(0x0C)
    OPCODE_0D = Opcode(0x0D)
    OPCODE_0E = Opcode(0x0E)
    OPCODE_0F = Opcode(0x0F)
    OPCODE_1E = Opcode(0x1E)
    OPCODE_1F = Opcode(0x1F)
    OPCODE_21 = Opcode(0x21)
    OPCODE_22 = Opcode(0x22)
    OPCODE_23 = Opcode(0x23)
    OPCODE_24 = Opcode(0x24)
    OPCODE_25 = Opcode(0x25)
    OPCODE_26 = Opcode(0x26)
    OPCODE_27 = Opcode(0x27)
    OPCODE_28 = Opcode(0x28)
    OPCODE_29 = Opcode(0x29)
    OPCODE_2A = Opcode(0x2A)
    OPCODE_2B = Opcode(0x2B)
    OPCODE_2C = Opcode(0x2C)
    OPCODE_2D = Opcode(0x2D)
    OPCODE_2E = Opcode(0x2E)
    OPCODE_2F = Opcode(0x2F)
    OPCODE_4B = Opcode(0x4B)
    OPCODE_4C = Opcode(0x4C)
    OPCODE_4D = Opcode(0x4D)
    OPCODE_4E = Opcode(0x4E)
    OPCODE_4F = Opcode(0x4F)
    OPCODE_A5 = Opcode(0xA5)
    OPCODE_A6 = Opcode(0xA6)
    OPCODE_A7 = Opcode(0xA7)
    OPCODE_A8 = Opcode(0xA8)
    OPCODE_A9 = Opcode(0xA9)
    OPCODE_AA = Opcode(0xAA)
    OPCODE_AB = Opcode(0xAB)
    OPCODE_AC = Opcode(0xAC)
    OPCODE_AD = Opcode(0xAD)
    OPCODE_AE = Opcode(0xAE)
    OPCODE_AF = Opcode(0xAF)
    OPCODE_B0 = Opcode(0xB0)
    OPCODE_B1 = Opcode(0xB1)
    OPCODE_B2 = Opcode(0xB2)
    OPCODE_B3 = Opcode(0xB3)
    OPCODE_B4 = Opcode(0xB4)
    OPCODE_B5 = Opcode(0xB5)
    OPCODE_B6 = Opcode(0xB6)
    OPCODE_B7 = Opcode(0xB7)
    OPCODE_B8 = Opcode(0xB8)
    OPCODE_B9 = Opcode(0xB9)
    OPCODE_BA = Opcode(0xBA)
    OPCODE_BB = Opcode(0xBB)
    OPCODE_BC = Opcode(0xBC)
    OPCODE_BD = Opcode(0xBD)
    OPCODE_BE = Opcode(0xBE)
    OPCODE_BF = Opcode(0xBF)
    OPCODE_C0 = Opcode(0xC0)
    OPCODE_C1 = Opcode(0xC1)
    OPCODE_C2 = Opcode(0xC2)
    OPCODE_C3 = Opcode(0xC3)
    OPCODE_C4 = Opcode(0xC4)
    OPCODE_C5 = Opcode(0xC5)
    OPCODE_C6 = Opcode(0xC6)
    OPCODE_C7 = Opcode(0xC7)
    OPCODE_C8 = Opcode(0xC8)
    OPCODE_C9 = Opcode(0xC9)
    OPCODE_CA = Opcode(0xCA)
    OPCODE_CB = Opcode(0xCB)
    OPCODE_CC = Opcode(0xCC)
    OPCODE_CD = Opcode(0xCD)
    OPCODE_CE = Opcode(0xCE)
    OPCODE_CF = Opcode(0xCF)
    OPCODE_D4 = Opcode(0xD4)
    OPCODE_D5 = Opcode(0xD5)
    OPCODE_D6 = Opcode(0xD6)
    OPCODE_D7 = Opcode(0xD7)
    OPCODE_D8 = Opcode(0xD8)
    OPCODE_D9 = Opcode(0xD9)
    OPCODE_DA = Opcode(0xDA)
    OPCODE_DB = Opcode(0xDB)
    OPCODE_DC = Opcode(0xDC)
    OPCODE_DD = Opcode(0xDD)
    OPCODE_DE = Opcode(0xDE)
    OPCODE_DF = Opcode(0xDF)
    OPCODE_E9 = Opcode(0xE9)
    OPCODE_EA = Opcode(0xEA)
    OPCODE_EB = Opcode(0xEB)
    OPCODE_ED = Opcode(0xED)
    OPCODE_EF = Opcode(0xEF)
    OPCODE_F6 = Opcode(0xF6)
    OPCODE_FC = Opcode(0xFC)


def expect_exception(opcode: Opcode) -> EOFException | None:
    """
    Returns exception that eof container reports when having this opcode in the middle of the code
    """
    if opcode._name_ in invalid_eof_opcodes or opcode in list(UndefinedOp):
        return EOFException.UNDEFINED_INSTRUCTION
    if opcode._name_ in halting_opcodes:
        return EOFException.UNREACHABLE_INSTRUCTIONS

    # RETF not allowed in first section
    if opcode == Op.RETF:
        return EOFException.INVALID_NON_RETURNING_FLAG
    return None


def make_data_portion(opcode: Opcode) -> bytes:
    """
    Construct data portion bytes for the opcode
    """
    return b"\x00" * opcode.data_portion_length


def make_opcode_valid_bytes(opcode: Opcode) -> Opcode | bytes:
    """
    Construct a valid stack and bytes for the opcode
    """
    if opcode._name_ in eof_opcodes and opcode != Op.RETF:
        if opcode == Op.CALLF:
            return opcode[1]
        return opcode[0]
    return opcode + make_data_portion(opcode)


def eof_opcode_stack(opcode: Opcode) -> int:
    """
    Eof opcode has special stack influence
    """
    if opcode._name_ in eof_opcodes:
        if opcode == Op.CALLF or opcode == Op.EXCHANGE:
            return 0
        return 1
    return 0


@pytest.mark.parametrize("opcode", list(Op) + list(UndefinedOp))
def test_all_opcodes_in_container(eof_test: EOFTestFiller, opcode: Opcode):
    """
    Test all opcodes inside valid container
    257 because 0x5B is duplicated
    """
    section_call = []
    if opcode == Op.CALLF:
        section_call = [
            Section.Code(
                code=Op.RETF,
                code_inputs=0,
                code_outputs=0,
                max_stack_height=0,
            )
        ]

    eof_code = Container(
        sections=[
            Section.Code(
                code=Op.PUSH1(00) * 20 + make_opcode_valid_bytes(opcode) + Op.STOP,
                max_stack_height=max(
                    20,
                    20
                    + opcode.pushed_stack_items
                    - opcode.popped_stack_items
                    + eof_opcode_stack(opcode),
                ),
            ),
            Section.Container(
                container=Container(
                    sections=[
                        Section.Code(code=Op.STOP),
                    ]
                )
            ),
        ]
        + section_call
        + [
            Section.Data("1122334455667788" * 4),
        ],
    )

    eof_test(
        data=eof_code,
        expect_exception=expect_exception(opcode),
    )
