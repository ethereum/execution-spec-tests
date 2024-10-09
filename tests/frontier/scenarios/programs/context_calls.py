"""
Define programs that will run all context opcodes for test scenarios
"""
import pytest

from ethereum_test_forks import Istanbul
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ..common import ProgramResult, ScenarioExpectOpcode

# Check that ADDRESS is really the code execution address in all scenarios
program_address = pytest.param(
    Op.MSTORE(0, Op.ADDRESS) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CODE_ADDRESS),
    id="program_ADDRESS",
)

# Check the BALANCE in all execution contexts
program_balance = pytest.param(
    Op.MSTORE(0, Op.BALANCE(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
    + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.BALANCE),
    id="program_BALANCE",
)

# Check that ORIGIN stays the same in all contexts
program_origin = pytest.param(
    Op.MSTORE(0, Op.ORIGIN) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.TX_ORIGIN),
    id="program_ORIGIN",
)


# Check the CALLER in all execution contexts
program_caller = pytest.param(
    Op.MSTORE(0, Op.CALLER) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CODE_CALLER),
    id="program_CALLER",
)

# Check the CALLVALUE in all execution contexts
program_callvalue = pytest.param(
    Op.MSTORE(0, Op.CALLVALUE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CALL_VALUE),
    id="program_CALLVALUE",
)

# Check the SELFBALANCE in all execution contexts
program_selfbalance = pytest.param(
    Op.MSTORE(0, Op.SELFBALANCE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.SELFBALANCE, from_fork=Istanbul),
    id="program_SELFBALANCE",
)

# Check that codecopy and codesize stays the same in all contexts
program_codecopy_codesize = pytest.param(
    Op.MSTORE(0, Op.CODESIZE) + Op.CODECOPY(0, 0, 30) + Op.RETURN(0, 32),
    ProgramResult(result=0x38600052601E600060003960206000F300000000000000000000000000000010),
    id="program_CODECOPY_CODESIZE",
)

# Check that chainid stays the same in all contexts
program_chainid = pytest.param(
    Op.MSTORE(0, Op.CHAINID) + Op.RETURN(0, 32),
    ProgramResult(result=1, from_fork=Istanbul),
    id="program_CHAINID",
)


# Check that extcodecopy and extcodesize stays the same in all contexts
# Need a static address in the state, origin with the code would work
# program_ext_codecopy_codesize = pytest.param(
#    Op.MSTORE(0, Op.EXTCODESIZE(Op.ADDRESS))
#    + Op.EXTCODECOPY(Op.ADDRESS, 0, 0, 30)
#    + Op.RETURN(0, 32),
#    ProgramResult(result=0x303B600052601E60006000303C60206000F30000000000000000000000000012),
#    id="program_EXTCODECOPY_EXTCODESIZE",
# )
