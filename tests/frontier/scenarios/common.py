"""Define Scenario structures and helpers for test_scenarios test."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

from _pytest.mark import ParameterSet

from ethereum_test_base_types import to_bytes
from ethereum_test_forks import Fork, Frontier
from ethereum_test_tools import Address, Alloc, Bytecode, Conditional
from ethereum_test_tools.vm.opcode import Opcodes as Op


@dataclass
class ScenarioDebug:
    """Debug selector for the development."""

    test_param: ParameterSet | None
    scenario_name: str


class ScenarioExpectOpcode(Enum):
    """Opcodes that are replaced to real values computed by the scenario."""

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
    GASLIMIT = 14


@dataclass
class ProgramResult:
    """
    Describe expected result of a program.

    Attributes:
        result (int | ScenarioExpectOpcode): The result of the program
        from_fork (Fork): The result is only valid from this fork (default: Frontier)
        static_support (bool): Can be verified in static context (default: True)

    """

    result: int | ScenarioExpectOpcode

    """The result is only valid from this fork"""
    from_fork: Fork = Frontier
    static_support: bool = True


@dataclass
class ScenarioEnvironment:
    """
    Scenario evm environment
    Each scenario must define an environment on which program is executed
    This is so post state verification could check results of evm opcodes.
    """

    code_address: Address  # Op.ADDRESS, address scope for program
    code_caller: Address  # Op.CALLER, caller of the program
    selfbalance: int  # Op.SELFBALANCE, balance of the environment of the program
    ext_balance: int  # Op.BALANCE(external) of fixed address deployed in state
    call_value: int  # Op.CALLVALUE of call that is done to the program
    call_dataload_0: int  # Op.CALLDATALOAD(0) expected result
    call_datasize: int  # Op.CALLDATASIZE expected result
    has_static: bool = False  # Weather scenario execution context is static


@dataclass
class ExecutionEnvironment:
    """Scenario execution environment which is determined by test."""

    fork: Fork
    gasprice: int
    origin: Address
    coinbase: Address
    timestamp: int
    number: int
    gaslimit: int


@dataclass
class ScenarioGeneratorInput:
    """
    Parameters for the scenario generator function.

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
    Describe test scenario that will be run in test for each program.

    Attributes:
        name (str): Scenario name for the test vector
        code (Address): Address that is an entry point for scenario code
        env (ScenarioEnvironment): Evm values for ScenarioExpectAddress map
        reverting (bool): If scenario reverts program execution, making result 0 (default: False)

    """

    name: str
    code: Address
    env: ScenarioEnvironment
    halts: bool = False


def translate_result(
    res: ProgramResult, env: ScenarioEnvironment, exec_env: ExecutionEnvironment
) -> int:
    """
    Translate expected program result code into concrete value,
    given the scenario evm environment and test execution environment.
    """
    if exec_env.fork < res.from_fork:
        return 0
    if not res.static_support and env.has_static:
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
        if res.result == ScenarioExpectOpcode.COINBASE:
            return int(exec_env.coinbase.hex(), 16)
        if res.result == ScenarioExpectOpcode.TIMESTAMP:
            return exec_env.timestamp
        if res.result == ScenarioExpectOpcode.NUMBER:
            return exec_env.number
        if res.result == ScenarioExpectOpcode.GASLIMIT:
            return exec_env.gaslimit
        if res.result == ScenarioExpectOpcode.SELFBALANCE:
            return int(env.selfbalance)

    return int(res.result)


def replace_special_calls_in_operation(
    pre: Alloc, operation: Bytecode, external_address: Address
) -> Bytecode:
    """
    Run find replace of some special calls to the contracts that we don't know at compile time
    replace 0xfff..fff address to external_address
    replace special call to 0xfff..ffe address to gas_hash_address contract.
    """
    gas_hash_address = make_gas_hash_contract(pre)
    invalid_opcode_contract = make_invalid_opcode_contract(pre)

    """Replace Op.CALL(Op.GAS, 0xfff..ffe, 0, 64, 32, 0, 0) to gas_hash_address"""
    """Replace Op.CALL(1000, 0xfff..ffd, 0, 64, 32, 0, 0) to invalid_opcode_contract"""
    """Replace BALANCE(0xfff..fff) to BALANCE(external_address) in operation"""
    """Replace EXTCODESIZE(0xfff..fff) to EXTCODESIZE(external_address) in operation"""
    """Replace EXTCODEHASH(0xfff..fff) to EXTCODEHASH(external_address) in operation"""
    """Replace EXTCODECOPY(0xfff..fff, ...) to EXTCODECOPY(external_address, ...)"""
    replace_list: List[Tuple[str, str]] = [
        (
            "600060006020604060007ffffffffffffffffffffffffffffffffffffffffffffffff"
            "ffffffffffffffffd620186a0f1",
            Op.CALL(10000, invalid_opcode_contract, 0, 64, 32, 0, 0).hex(),
        ),
        (
            "600060006020604060007ffffffffffffffffffffffffffffffffffffffffffffffff"
            "ffffffffffffffffe5af1",
            Op.CALL(Op.SUB(Op.GAS, 200000), gas_hash_address, 0, 64, 32, 0, 0).hex(),
        ),
        (
            "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff31",
            Op.BALANCE(external_address).hex(),
        ),
        (
            "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff3b",
            Op.EXTCODESIZE(external_address).hex(),
        ),
        (
            "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff3f",
            Op.EXTCODEHASH(external_address).hex(),
        ),
        (
            "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff3c",
            "3c".join(Op.BALANCE(external_address).hex().rsplit("31", 1)),
        ),
    ]
    for find, replace in replace_list:
        if find in operation.hex():
            new_operation_hex = operation.hex().replace(
                find,
                replace,
            )
            operation = Bytecode(
                bytes_or_byte_code_base=to_bytes(new_operation_hex),
                popped_stack_items=0,
                pushed_stack_items=0,
            )
    return operation


def make_gas_hash_contract(pre: Alloc) -> Address:
    """
    Contract that spends unique amount of gas based on input
    Used for the values we can't predict, can be gas consuming on high values
    So that if we can't check exact value in expect section,
    we at least could spend unique gas amount.
    """
    gas_hash_address = pre.deploy_contract(
        code=Op.MSTORE(0, 0)
        + Op.JUMPDEST
        + Op.CALLDATACOPY(63, Op.MLOAD(0), 1)
        + Op.JUMPDEST
        + Conditional(
            condition=Op.EQ(Op.MLOAD(32), 0),
            if_true=Op.MSTORE(0, Op.ADD(1, Op.MLOAD(0)))
            + Conditional(
                condition=Op.GT(Op.MLOAD(0), 32),
                if_true=Op.RETURN(0, 0),
                if_false=Op.JUMP(5),
            ),
            if_false=Op.MSTORE(32, Op.SUB(Op.MLOAD(32), 1)) + Op.JUMP(14),
        )
    )
    return gas_hash_address


def make_invalid_opcode_contract(pre: Alloc) -> Address:
    """
    Deploy a contract that will execute any asked byte as an opcode from calldataload
    With 0-ed input stack of 10 elements, valid for opcodes starting at 0x0C.
    """
    invalid_opcode_caller = pre.deploy_contract(
        code=Op.PUSH0 * 10
        + Op.JUMP(Op.SUB(Op.MUL(2, Op.CALLDATALOAD(0)), 1))  # here pc is 19
        + Op.JUMPDEST * 4
        + sum(
            [
                Bytecode(bytes([opcode]), popped_stack_items=0, pushed_stack_items=0) + Op.JUMPDEST
                for opcode in range(0x0C, 0xFF)
            ],
        )
    )
    return invalid_opcode_caller
