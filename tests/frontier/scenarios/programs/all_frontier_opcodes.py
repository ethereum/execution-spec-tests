"""
Define a program for scenario test that executes all frontier opcodes and entangles it's result
"""

import pytest

from ethereum_test_tools import Bytecode, Conditional
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..common import ProgramResult

# Opcodes that are not in Frontier
# 1b - SHL
# 1c - SHR
# 1d - SAR


def make_all_opcode_program() -> Bytecode:
    """Make a program that call each Frontier opcode and verifies it's result"""
    code: Bytecode = (
        # Test opcode 01 - ADD
        Conditional(
            condition=Op.EQ(Op.ADD(1, 1), 2),
            if_true=Op.MSTORE(0, 2),
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test opcode 02 - MUL
        + Conditional(
            condition=Op.EQ(
                Op.MUL(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 2),
                0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE,
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 03 - SUB
        + Conditional(
            condition=Op.EQ(
                Op.SUB(0, 1),
                0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 04 - DIV
        + Conditional(
            condition=Op.AND(Op.EQ(Op.DIV(1, 2), 0), Op.EQ(Op.DIV(10, 2), 5)),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 05 - SDIV
        + Conditional(
            condition=Op.EQ(
                Op.SDIV(
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE,
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                ),
                2,
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 06 - MOD
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.MOD(10, 3), 1),
                Op.EQ(
                    Op.MOD(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF8,
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD,
                    ),
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF8,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 07 - SMOD
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.SMOD(10, 3), 1),
                Op.EQ(
                    Op.SMOD(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF8,
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD,
                    ),
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 08 - ADDMOD
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.ADDMOD(10, 10, 8), 4),
                Op.EQ(
                    Op.ADDMOD(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                        2,
                        2,
                    ),
                    1,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 09 - MULMOD
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.MULMOD(10, 10, 8), 4),
                Op.EQ(
                    Op.MULMOD(
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                        12,
                    ),
                    9,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 0A - EXP
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.EXP(10, 2), 100),
                Op.EQ(
                    Op.EXP(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD, 2),
                    9,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 0B - SIGNEXTEND
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.SIGNEXTEND(0, 0xFF),
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                ),
                Op.EQ(
                    Op.SIGNEXTEND(0, 0x7F),
                    0x7F,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 10 - LT
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.LT(9, 10),
                    1,
                ),
                Op.EQ(
                    Op.LT(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0),
                    0,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 11 - GT
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.GT(9, 10),
                    0,
                ),
                Op.EQ(
                    Op.GT(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0),
                    1,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 12 - SLT
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.SLT(9, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
                    0,
                ),
                Op.EQ(
                    Op.SLT(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0),
                    1,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 13 - SGT
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.SGT(10, 10),
                    0,
                ),
                Op.EQ(
                    Op.SGT(0, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF),
                    1,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 14 - EQ Skip
        # Test 15 - ISZero
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.ISZERO(10), 0),
                Op.EQ(Op.ISZERO(0), 1),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 16 - AND Skip
        # Test 17 - OR
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.OR(0xF0, 0xF), 0xFF),
                Op.EQ(Op.OR(0xFF, 0xFF), 0xFF),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 18 - XOR
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.XOR(0xF0, 0xF), 0xFF),
                Op.EQ(Op.XOR(0xFF, 0xFF), 0),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 19 - NOT
        + Conditional(
            condition=Op.AND(
                Op.EQ(
                    Op.NOT(0), 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
                ),
                Op.EQ(
                    Op.NOT(0xFFFFFFFFFFFF),
                    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000,
                ),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 1A - BYTE
        + Conditional(
            condition=Op.AND(
                Op.EQ(Op.BYTE(31, 0xFF), 0xFF),
                Op.EQ(Op.BYTE(30, 0xFF00), 0xFF),
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # Test 20 - SHA3
        + Op.MSTORE(0, 0xFFFFFFFF)
        + Conditional(
            condition=Op.EQ(
                Op.SHA3(28, 4),
                0x29045A592007D0C246EF02C2223570DA9522D0CF0F73282C79A1BC8F0BB2C238,
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # 50 POP
        # 51 MLOAD
        # 52 MSTORE
        # 53 MSTORE8
        + Op.MSTORE(0, 0)
        + Op.MSTORE8(0, 0xFFFF)
        + Conditional(
            condition=Op.EQ(
                Op.MLOAD(0),
                0xFF00000000000000000000000000000000000000000000000000000000000000,
            ),
            if_true=Op.JUMPDEST,
            if_false=Op.MSTORE(0, 0) + Op.RETURN(0, 32),
        )
        # 54 SLOAD
        # 55 SSTORE # can't use because of static contexts
        # 56 JUMP
        # 57 JUMPI
        # 58 PC
        # 59 MSIZE
        # 5A GAS
        # 5B JUMPDEST
        + Op.MSTORE(0, 1)
        + Op.RETURN(0, 32)
    )
    return code


program_all_frontier_opcodes = pytest.param(
    make_all_opcode_program(),
    ProgramResult(result=1),
    id="program_ALL_FRONTIER_OPCODES",
)
