"""
Call every possible opcode and test that the subcall is successful
if the opcode is supported by the fork and fails otherwise.
"""

from typing import List

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .common import (
    ExecutionEnvironment,
    ProgramResult,
    Scenario,
    ScenarioDebug,
    ScenarioGeneratorInput,
    replace_special_calls_in_operation,
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
    program_mcopy,
    program_number,
    program_origin,
    program_push0,
    program_returndatacopy,
    program_returndatasize,
    program_selfbalance,
    program_timestamp,
    program_tload,
)
from .programs.invalid_opcodes import program_invalid
from .programs.static_violation import (
    program_logs,
    program_sstore_sload,
    program_suicide,
    program_tstore_tload,
)
from .scenarios.call_combinations import ScenariosCallCombinations
from .scenarios.create_combinations import scenarios_create_combinations
from .scenarios.revert_combinations import scenarios_revert_combinations

REFERENCE_SPEC_GIT_PATH = "N/A"

REFERENCE_SPEC_VERSION = "N/A"


@pytest.fixture
def scenarios(fork: Fork, pre: Alloc, operation: Bytecode, debug: ScenarioDebug) -> List[Scenario]:
    """
    This is the main parametrization vector
    Define list of contracts that execute scenarios for a given operation
    """
    list: List[Scenario] = []

    """select only debug program if set"""
    if debug.test_param is not None:
        debug_program = debug.test_param.values[0]
        if hasattr(debug_program, "hex") and operation.hex() != debug_program.hex():
            return list

    """Deploy external address to test ext opcodes"""
    external_balance = 123
    external_address = pre.deploy_contract(code=Op.ADD(1, 1), balance=external_balance)

    operation = replace_special_calls_in_operation(pre, operation, external_address)

    input: ScenarioGeneratorInput = ScenarioGeneratorInput(
        fork=fork,
        pre=pre,
        operation_code=operation,
        external_address=external_address,
        external_balance=external_balance,
    )

    call_combinations = ScenariosCallCombinations(input).generate()
    for combination in call_combinations:
        if not debug.scenario_name or combination.name == debug.scenario_name:
            list.append(combination)

    call_combinations = scenarios_create_combinations(input)
    for combination in call_combinations:
        if not debug.scenario_name or combination.name == debug.scenario_name:
            list.append(combination)

    revert_combinations = scenarios_revert_combinations(input)
    for combination in revert_combinations:
        if not debug.scenario_name or combination.name == debug.scenario_name:
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
    # select program to debug (program, "scenario_name")
    # program=None select all programs
    # scenario_name="" select all scenarios
    "debug",
    [ScenarioDebug(None, scenario_name="")],
    ids=["debug"],
)
@pytest.mark.parametrize(
    "operation, expected_result",
    [
        # invalid opcodes
        program_invalid,
        # static violation programs
        program_sstore_sload,
        program_tstore_tload,
        program_logs,
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
        program_blockhash,  # fails in state mode in py-t8n
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
        program_tload,
        program_mcopy,
        program_push0,
        program_suicide,
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
    # Skip disabled scenarios in debug mode
    if len(scenarios) == 0:
        return

    tx_env = Environment()
    post = Storage()
    result_slot = post.store_next(1, hint="runner_result")

    tx_origin: Address = pre.fund_eoa()
    tx_gasprice: int = 10
    exec_env = ExecutionEnvironment(
        fork=fork,
        origin=tx_origin,
        gasprice=tx_gasprice,
        timestamp=tx_env.timestamp,
        number=tx_env.number,
        gaslimit=tx_env.gas_limit,
        coinbase=tx_env.fee_recipient,
    )

    def make_result(scenario: Scenario) -> int:
        """Make Scenario post result"""
        if scenario.halts:
            return post.store_next(0, hint=scenario.name)
        else:
            return post.store_next(
                translate_result(expected_result, scenario.env, exec_env), hint=scenario.name
            )

    runner_contract = pre.deploy_contract(
        code=sum(
            Op.MSTORE(0, 0)
            + Op.CALL(10000000, scenario.code, 0, 0, 0, 0, 32)
            + Op.SSTORE(make_result(scenario), Op.MLOAD(0))
            for scenario in scenarios
        )
        + Op.SSTORE(result_slot, 1),
        storage={
            result_slot: 0xFFFF,
        },
    )

    tx = Transaction(
        sender=tx_origin,
        gas_limit=500_000_000,
        gas_price=tx_gasprice,
        to=runner_contract,
        data=b"0x11223344",
        value=0,
        protected=False,
    )
    state_test(
        env=tx_env,
        pre=pre,
        post={
            runner_contract: Account(
                storage=post,
            )
        },
        tx=tx,
    )
