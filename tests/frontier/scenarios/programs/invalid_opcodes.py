"""Define programs that can not be run in static context."""

import pytest

from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..common import ProgramResult, SpecialAddress

program_invalid = pytest.param(
    Op.MSTORE(0, Op.CALL(5000, SpecialAddress.INVALID_CALL_ADDRESS, 0, 64, 32, 100, 32))
    + Op.RETURN(100, 32),
    ProgramResult(result=1),
    id="program_INVALID",
)
