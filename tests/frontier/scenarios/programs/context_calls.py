"""
Define programs that will run all context opcodes for test scenarios
"""

import pytest

from ethereum_test_forks import Byzantium, Cancun, Constantinople, Istanbul, London, Shanghai
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

# Check the CALLDATALOAD in all execution contexts
program_calldataload = pytest.param(
    Op.MSTORE(0, Op.CALLDATALOAD(0)) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CALL_DATALOAD_0),
    id="program_CALLDATALOAD",
)

# Check the CALLDATASIZE in all execution contexts
program_calldatasize = pytest.param(
    Op.MSTORE(0, Op.CALLDATASIZE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CALL_DATASIZE),
    id="program_CALLDATASIZE",
)

# Check the CALLDATACOPY in all execution contexts
program_calldatacopy = pytest.param(
    Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.CALL_DATALOAD_0),
    id="program_CALLDATACOPY",
)

# Check that codecopy and codesize stays the same in all contexts
program_codecopy_codesize = pytest.param(
    Op.MSTORE(0, Op.CODESIZE) + Op.CODECOPY(0, 0, 30) + Op.RETURN(0, 32),
    ProgramResult(result=0x38600052601E600060003960206000F300000000000000000000000000000010),
    id="program_CODECOPY_CODESIZE",
)

# Check that gasprice stays the same in all contexts
program_gasprice = pytest.param(
    Op.MSTORE(0, Op.GASPRICE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.GASPRICE),
    id="program_GASPRICE",
)

# Check that extcodesize and extcodecopy of pre deployed contract stay the same in all contexts
program_ext_codecopy_codesize = pytest.param(
    Op.MSTORE(
        0, Op.EXTCODESIZE(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    )
    + Op.EXTCODECOPY(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0, 0, 30)
    + Op.RETURN(0, 32),
    ProgramResult(result=0x6001600101000000000000000000000000000000000000000000000000000005),
    id="program_EXTCODECOPY_EXTCODESIZE",
)

# Check that returndatasize stays the same in all contexts
program_returndatasize = pytest.param(
    Op.MSTORE(0, Op.RETURNDATASIZE)
    + Op.CALL(100000, 2, 0, 0, 10, 32, 20)
    + Op.MSTORE(0, Op.ADD(Op.MLOAD(0), Op.RETURNDATASIZE))
    + Op.RETURN(0, 32),
    ProgramResult(result=32, from_fork=Byzantium),
    id="program_RETURNDATASIZE",
)

# Check that returndatacopy stays the same in all contexts
program_returndatacopy = pytest.param(
    Op.CALL(100000, 2, 0, 0, 10, 32, 20) + Op.RETURNDATACOPY(0, 0, 32) + Op.RETURN(0, 32),
    ProgramResult(
        result=0x1D448AFD928065458CF670B60F5A594D735AF0172C8D67F22A81680132681CA,
        from_fork=Byzantium,
    ),
    id="program_RETURNDATACOPY",
)

# Check that extcodehash stays the same in all contexts
program_extcodehash = pytest.param(
    Op.MSTORE(
        0, Op.EXTCODEHASH(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
    )
    + Op.RETURN(0, 32),
    ProgramResult(
        result=0x8C634A8B28DD46F5DCB9A9F5DA1FAED26D0FB5ED98F3873A29AD27AAAFFDE0E4,
        from_fork=Constantinople,
    ),
    id="program_EXTCODEHASH",
)

# Check that blockhash stays the same in all contexts
# Need a way to pre calculate at least hash of block 0
program_blockhash = pytest.param(
    # Calculate gas hash of Op.BLOCKHASH(0) value
    Op.MSTORE(64, Op.BLOCKHASH(0))
    + Op.CALL(
        Op.GAS, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE, 0, 64, 32, 0, 0
    )
    + Op.MSTORE(0, 1)
    + Op.RETURN(0, 32),
    ProgramResult(result=1),
    id="program_BLOCKHASH",
)

# Need a way to pre calculate coinbase
program_coinbase = pytest.param(
    Op.MSTORE(0, Op.COINBASE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.COINBASE),
    id="program_COINBASE",
)

program_timestamp = pytest.param(
    Op.MSTORE(0, Op.TIMESTAMP) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.TIMESTAMP),
    id="program_TIMESTAMP",
)

program_number = pytest.param(
    Op.MSTORE(0, Op.NUMBER) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.NUMBER),
    id="program_NUMBER",
)

program_difficulty_randao = pytest.param(
    # Calculate gas hash of DIFFICULTY value
    Op.MSTORE(0, Op.PREVRANDAO)
    + Op.MSTORE(64, Op.PREVRANDAO)
    + Op.CALL(
        Op.GAS, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE, 0, 64, 32, 0, 0
    )
    + Op.MSTORE(0, 1)
    + Op.RETURN(0, 32),
    ProgramResult(result=1),
    id="program_DIFFICULTY",
)

program_gaslimit = pytest.param(
    Op.MSTORE(0, Op.GASLIMIT) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.GASLIMIT),
    id="program_GASLIMIT",
)

# Check that chainid stays the same in all contexts
program_chainid = pytest.param(
    Op.MSTORE(0, Op.CHAINID) + Op.RETURN(0, 32),
    ProgramResult(result=1, from_fork=Istanbul),
    id="program_CHAINID",
)

# Check the SELFBALANCE in all execution contexts
program_selfbalance = pytest.param(
    Op.MSTORE(0, Op.SELFBALANCE) + Op.RETURN(0, 32),
    ProgramResult(result=ScenarioExpectOpcode.SELFBALANCE, from_fork=Istanbul),
    id="program_SELFBALANCE",
)

program_basefee = pytest.param(
    # Calculate gas hash of BASEFEE value
    Op.MSTORE(64, Op.BASEFEE)
    + Op.CALL(
        Op.GAS, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE, 0, 64, 32, 0, 0
    )
    + Op.MSTORE(0, 1)
    + Op.RETURN(0, 32),
    ProgramResult(result=1, from_fork=London),
    id="program_BASEFEE",
)

program_blobhash = pytest.param(
    Op.MSTORE(0, Op.BLOBHASH(0)) + Op.RETURN(0, 32),
    ProgramResult(result=0, from_fork=Cancun),
    id="program_BLOBHASH",
)

program_blobbasefee = pytest.param(
    # Calculate gas hash of BLOBBASEFEE value
    Op.MSTORE(64, Op.BLOBBASEFEE)
    + Op.CALL(
        Op.GAS, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE, 0, 64, 32, 0, 0
    )
    + Op.MSTORE(0, 1)
    + Op.RETURN(0, 32),
    ProgramResult(result=1, from_fork=Cancun),
    id="program_BLOBBASEFEE",
)

program_tload = pytest.param(
    Op.MSTORE(0, Op.TLOAD(0)) + Op.RETURN(0, 32),
    ProgramResult(result=0, from_fork=Cancun),
    id="program_TLOAD",
)

program_mcopy = pytest.param(
    Op.MSTORE(0, 0)
    + Op.MSTORE(32, 0x000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F)
    + Op.MCOPY(0, 32, 32)
    + Op.RETURN(0, 32),
    ProgramResult(
        result=0x000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F, from_fork=Cancun
    ),
    id="program_MCOPY",
)

program_push0 = pytest.param(
    Op.PUSH1(10) + Op.PUSH0 + Op.MSTORE + Op.RETURN(0, 32),
    ProgramResult(result=10, from_fork=Shanghai),
    id="program_PUSH0",
)
