"""
Call every possible opcode and test that the subcall is successful
if the opcode is supported by the fork and fails otherwise.
"""

from typing import Dict, List, Tuple

import pytest

from ethereum_test_base_types import Number, to_bytes
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    Hash,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .common import (
    ExecutionEnvironment,
    ProgramResult,
    Scenario,
    ScenarioGeneratorInput,
    translate_result,
)
from .programs.all_frontier_opcodes import program_all_frontier_opcodes
from .programs.context_calls import (
    program_address,
    program_balance,
    program_basefee,
    program_blobbasefee,
    program_blobhash,
    program_blockhash,
    program_calldatacopy,
    program_calldataload,
    program_calldatasize,
    program_caller,
    program_callvalue,
    program_chainid,
    program_codecopy_codesize,
    program_coinbase,
    program_difficulty_randao,
    program_ext_codecopy_codesize,
    program_extcodehash,
    program_gaslimit,
    program_gasprice,
    program_number,
    program_origin,
    program_returndatacopy,
    program_returndatasize,
    program_selfbalance,
    program_timestamp,
)
from .scenarios.call_combinations import ScenariosCallCombinations
from .scenarios.create_combinations import scenarios_create_combinations
from .scenarios.revert_combinations import scenarios_revert_combinations

REFERENCE_SPEC_GIT_PATH = "N/A"
REFERENCE_SPEC_VERSION = "N/A"


@pytest.fixture
def scenarios(fork: Fork, pre: Alloc, operation: Bytecode) -> List[Scenario]:
    """
    This is the main parametrization vector
    Define list of contracts that execute scenarios for a given operation
    """
    list: List[Scenario] = []

    """Deploy external address to test ext opcodes"""
    external_address = pre.deploy_contract(code=Op.ADD(1, 1), balance=123)

    """Replace BALANCE(0xfff..fff) to BALANCE(external_address) in operation"""
    """Replace EXTCODESIZE(0xfff..fff) to EXTCODESIZE(external_address) in operation"""
    """Replace EXTCODEHASH(0xfff..fff) to EXTCODEHASH(external_address) in operation"""
    """Replace EXTCODECOPY(0xfff..fff, ...) to EXTCODECOPY(external_address, ...)"""
    replace_list: List[Tuple[str, str]] = [
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
    # raise Exception(operation.hex())

    input: ScenarioGeneratorInput = ScenarioGeneratorInput(
        fork=fork,
        pre=pre,
        operation_code=operation,
        external_address=external_address,
        external_balance=123,
    )

    call_combinations = ScenariosCallCombinations(input).generate()
    for combination in call_combinations:
        # if combination.name == "scenario_STATICCALL_CALL":
        list.append(combination)

    call_combinations = scenarios_create_combinations(input)
    for combination in call_combinations:
        #    if combination.name == "scenario_CREATE2_then_CALL":
        list.append(combination)

    revert_combinations = scenarios_revert_combinations(input)
    for combination in revert_combinations:
        list.append(combination)

    """
        // 21. 0x00FD  Run the code, call a contract that reverts, then run again
        // 22. 0x00FE  Run the code, call a contract that goes out of gas, then run again
        // 23. 0x00FF  Run the code, call a contract that self-destructs, then run again
        // 34. 0x60BACCFA57 Call recurse to the limit
    """

    return list


@pytest.mark.valid_from("Frontier")
@pytest.mark.parametrize(
    "operation, expected_result",
    [
        # 00 - 20
        program_all_frontier_opcodes,
        # 30
        program_address,
        program_balance,
        program_origin,
        program_caller,
        program_callvalue,
        program_calldataload,
        program_calldatasize,
        program_calldatacopy,
        program_codecopy_codesize,
        program_gasprice,
        program_ext_codecopy_codesize,
        program_returndatasize,
        program_returndatacopy,
        program_extcodehash,
        # 40
        program_blockhash,  # can't use because we are in state test mode
        program_coinbase,
        program_timestamp,
        program_number,
        program_difficulty_randao,
        program_gaslimit,
        program_chainid,
        program_selfbalance,
        program_basefee,
        program_blobhash,
        program_blobbasefee,
    ],
)
def test_scenarios(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    expected_result: ProgramResult,
    scenarios,
):
    """
    Test given operation in different scenarios
    Verify that it's return value equal to expected result on every scenario,
    that is valid for the given fork

    Note: Don't use pytest parametrize for scenario production, because scenarios will be complex
    Generate one test file for [each operation] * [each scenario] to save space
    As well as operations will be complex too
    """
    tx_env = Environment()
    tx_env.set_fork_requirements(fork)

    tx_origin: Address = pre.fund_eoa()
    tx_gasprice: int = 10
    code_worked = 1000
    exec_env = ExecutionEnvironment(
        fork=fork,
        origin=tx_origin,
        gasprice=tx_gasprice,
        timestamp=tx_env.timestamp,
        number=tx_env.number,
        gaslimit=tx_env.gas_limit,
        coinbase=tx_env.fee_recipient,
        # how to pre calculate this values:
        blob_basefee=0,  # because we are in frontier test folder
        blobhash_0=Hash(0),  # because we are in frontier test folder
        blockhash_0=Hash(0),
        difficulty_randao=0 if tx_env.difficulty is None else int(tx_env.difficulty.hex(), 16),
        basefee=0 if tx_env.base_fee_per_gas is None else int(tx_env.base_fee_per_gas.hex(), 16),
    )

    runner_contract = pre.deploy_contract(
        code=sum(
            Op.MSTORE(0, 0)
            + Op.CALL(1000000, scenario.code, 0, 0, 0, 0, 32)
            + Op.SSTORE(index, Op.MLOAD(0))
            for index, (scenario) in enumerate(scenarios)
        )
        + Op.SSTORE(code_worked, 1)
    )
    post = {
        runner_contract: Account(
            storage={
                **{
                    index: (
                        translate_result(expected_result, scenario.env, exec_env)
                        if not scenario.reverting
                        else 0
                    )
                    for index, (scenario) in enumerate(scenarios)
                },
                code_worked: 1,
            }
        ),
    }

    hint: Dict[int, str] = {}
    for index, (scenario) in enumerate(scenarios):
        hint[index] = scenario.name

    tx = Transaction(
        sender=tx_origin,
        gas_limit=500_000_000,
        gas_price=tx_gasprice,
        to=runner_contract,
        data=b"",
        value=0,
        protected=False,
    )

    state_test(env=tx_env, pre=pre, post=post, tx=tx, post_hint=hint)
