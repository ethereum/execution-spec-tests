"""
Define Scenario class for test_scenarios test
"""

from dataclasses import dataclass
from enum import Enum

from ethereum_test_forks import Fork, Frontier
from ethereum_test_tools import Address, Alloc, Bytecode, Hash


class ScenarioExpectOpcode(Enum):
    """Opcodes that are replaced to real values computed by the scenario"""

    TX_ORIGIN = 1
    CODE_ADDRESS = 2
    CODE_CALLER = 3
    SELFBALANCE = 4
    BALANCE = 5
    CALL_VALUE = 6
    CALL_DATALOAD_0 = 7
    CALL_DATASIZE = 8
    GASPRICE = 9
    BLOCKHASH_0 = 10
    COINBASE = 11
    TIMESTAMP = 12
    NUMBER = 13
    DIFFICULTY_RANDAO = 14
    GASLIMIT = 15
    BASEFEE = 16
    BLOBHASH_0 = 17
    BLOBBASEFEE = 18


@dataclass
class ProgramResult:
    """
    Describe expected result of a program

    Attributes:
        result (int | ScenarioExpectOpcode): The result of the program
        from_fork (Fork): The result is only valid from this fork (default: Frontier)
    """

    result: int | ScenarioExpectOpcode

    """The result is only valid from this fork"""
    from_fork: Fork = Frontier


@dataclass
class ScenarioEnvironment:
    """
    Scenario evm environment
    Each scenario must define an environment on which program is executed
    This is so post state verification could check results of evm opcodes
    """

    code_address: Address  # Op.ADDRESS, address scope for program
    code_caller: Address  # Op.CALLER, caller of the program
    selfbalance: int  # Op.SELFBALANCE, balance of the environment of the program
    ext_balance: int  # Op.BALANCE(external) of fixed address deployed in state
    call_value: int  # Op.CALLVALUE of call that is done to the program
    call_dataload_0: int  # Op.CALLDATALOAD(0) expected result
    call_datasize: int  # Op.CALLDATASIZE expected result


@dataclass
class ExecutionEnvironment:
    """
    Scenario execution environment which is determined by test
    """

    fork: Fork
    gasprice: int
    origin: Address
    coinbase: Address
    blockhash_0: Hash
    timestamp: int
    number: int
    difficulty_randao: int
    gaslimit: int
    basefee: int
    blobhash_0: Hash
    blob_basefee: int


@dataclass
class ScenarioGeneratorInput:
    """
    Parameters for the scenario generator function

    Attributes:
        fork (Fork): Fork for which we ask to generate scenarios
        pre (Alloc): Access to the state to be able to deploy contracts into pre
        operation (Bytecode): Evm bytecode program that will be tested
        external_address (Address): Static external address for ext opcodes
    """

    fork: Fork
    pre: Alloc
    operation_code: Bytecode
    external_address: Address
    external_balance: int


@dataclass
class Scenario:
    """
    Describe test scenario that will be run in test for each program

    Attributes:
        name (str): Scenario name for the test vector
        code (Address): Address that is an entry point for scenario code
        env (ScenarioEnvironment): Evm values for ScenarioExpectAddress map
        reverting (bool): If scenario reverts program execution, making result 0 (default: False)
    """

    name: str
    code: Address
    env: ScenarioEnvironment
    reverting: bool = False


def translate_result(
    res: ProgramResult, env: ScenarioEnvironment, exec_env: ExecutionEnvironment
) -> int:
    """
    Translate expected program result code into concrete value,
    given the scenario evm environment and test execution environment
    """
    if exec_env.fork < res.from_fork:
        return 0
    if isinstance(res.result, ScenarioExpectOpcode):
        if res.result == ScenarioExpectOpcode.TX_ORIGIN:
            return int(exec_env.origin.hex(), 16)
        if res.result == ScenarioExpectOpcode.CODE_ADDRESS:
            return int(env.code_address.hex(), 16)
        if res.result == ScenarioExpectOpcode.CODE_CALLER:
            return int(env.code_caller.hex(), 16)
        if res.result == ScenarioExpectOpcode.BALANCE:
            return int(env.ext_balance)
        if res.result == ScenarioExpectOpcode.CALL_VALUE:
            return int(env.call_value)
        if res.result == ScenarioExpectOpcode.CALL_DATALOAD_0:
            return env.call_dataload_0
        if res.result == ScenarioExpectOpcode.CALL_DATASIZE:
            return env.call_datasize
        if res.result == ScenarioExpectOpcode.GASPRICE:
            return exec_env.gasprice
        if res.result == ScenarioExpectOpcode.BLOCKHASH_0:
            return int(exec_env.blockhash_0.hex(), 16)
        if res.result == ScenarioExpectOpcode.COINBASE:
            return int(exec_env.coinbase.hex(), 16)
        if res.result == ScenarioExpectOpcode.TIMESTAMP:
            return exec_env.timestamp
        if res.result == ScenarioExpectOpcode.NUMBER:
            return exec_env.number
        if res.result == ScenarioExpectOpcode.DIFFICULTY_RANDAO:
            return exec_env.difficulty_randao
        if res.result == ScenarioExpectOpcode.GASLIMIT:
            return exec_env.gaslimit
        if res.result == ScenarioExpectOpcode.SELFBALANCE:
            return int(env.selfbalance)
        if res.result == ScenarioExpectOpcode.BASEFEE:
            return exec_env.basefee
        if res.result == ScenarioExpectOpcode.BLOBHASH_0:
            return int(exec_env.blobhash_0.hex(), 16)
        if res.result == ScenarioExpectOpcode.BLOBBASEFEE:
            return exec_env.blob_basefee

    return res.result
