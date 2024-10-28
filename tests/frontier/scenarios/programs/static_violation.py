"""
Define programs that can not be run in static context
"""

import pytest

from ethereum_test_forks import Cancun
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..common import ProgramResult

program_sstore_sload = pytest.param(
    Op.SSTORE(0, 11)
    + Op.MSTORE(0, Op.ADD(Op.MLOAD(0), Op.SLOAD(0)))
    + Op.SSTORE(0, 5)
    + Op.MSTORE(0, Op.ADD(Op.MLOAD(0), Op.SLOAD(0)))
    + Op.RETURN(0, 32),
    ProgramResult(result=16, static_support=False),
    id="program_SSTORE_SLOAD",
)

program_tstore_tload = pytest.param(
    Op.TSTORE(0, 11) + Op.MSTORE(0, Op.TLOAD(0)) + Op.RETURN(0, 32),
    ProgramResult(result=11, static_support=False, from_fork=Cancun),
    id="program_TSTORE_TLOAD",
)

program_logs = pytest.param(
    Op.MSTORE(0, 0x1122334455667788991011121314151617181920212223242526272829303132)
    + Op.LOG0(0, 1)
    + Op.LOG1(1, 1, 0x1000)
    + Op.LOG2(2, 1, 0x2000, 0x2001)
    + Op.LOG3(3, 1, 0x3000, 0x3001, 0x3002)
    + Op.LOG4(4, 1, 0x4000, 0x4001, 0x4002, 0x4003)
    + Op.MSTORE(0, 1)
    + Op.RETURN(0, 32),
    ProgramResult(result=1, static_support=False),
    id="program_LOGS",
)

program_suicide = pytest.param(
    Op.MSTORE(0, 1) + Op.SELFDESTRUCT(0) + Op.RETURN(0, 32),
    ProgramResult(result=0, static_support=False),
    id="program_SUICIDE",
)
