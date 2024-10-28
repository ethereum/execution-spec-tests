"""
Define programs that can not be run in static context
"""

import pytest

from ethereum_test_tools import Bytecode
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..common import ProgramResult

invalid_opcode_ranges = [
    range(0x0C, 0x10),
    range(0x1E, 0x20),
    range(0x21, 0x30),
    range(0x4B, 0x50),
    range(0xA5, 0xF0),
    range(0xF6, 0xFA),
    range(0xFB, 0xFD),
    range(0xFE, 0xFF),
]


def make_all_invalid_opcode_calls() -> Bytecode:
    """Call special contract to initiate all invalid opcode instruction"""
    invalid_opcode_caller = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFD

    code = Bytecode(
        sum(
            [
                Op.MSTORE(64, opcode)
                + Op.MSTORE(32, Op.CALL(100000, invalid_opcode_caller, 0, 64, 32, 0, 0))
                + Op.MSTORE(0, Op.ADD(Op.MLOAD(0), Op.MLOAD(32)))
                for opcode_range in invalid_opcode_ranges
                for opcode in opcode_range
            ],
            start=Bytecode(),
        )
        # If any of invalid instructions works, mstore[0] will be > 1
        + Op.MSTORE(0, Op.ADD(Op.MLOAD(0), 1))
        + Op.RETURN(0, 32)
    )
    return code


program_invalid = pytest.param(
    make_all_invalid_opcode_calls(),
    ProgramResult(result=1),
    id="program_INVALID",
)
