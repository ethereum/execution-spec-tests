"""
Define Scenario class for test_scenarios test
"""
from dataclasses import dataclass
from enum import Enum

from ethereum_test_forks import Fork, Frontier
from ethereum_test_tools import Address, Alloc, Bytecode


class ScenarioExpectOpcode(Enum):
    """Opcodes that are replaced to real values computed by the scenario"""

    TX_ORIGIN = 1
    CODE_ADDRESS = 2
    CODE_CALLER = 3
    SELFBALANCE = 4
    BALANCE = 5
    CALL_VALUE = 6


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
