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
    Block,
    BlockchainTestFiller,
    Bytecode,
    Environment,
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
def scenario_input(fork: Fork, pre: Alloc, operation: Bytecode) -> ScenarioGeneratorInput:
    """Prepare the state for scenario."""
    external_balance = 123
    external_address = pre.deploy_contract(code=Op.ADD(1, 1), balance=external_balance)
    operation = replace_special_calls_in_operation(pre, fork, operation, external_address)
    return ScenarioGeneratorInput(
        fork=fork,
        pre=pre,
        operation_code=operation,
        external_address=external_address,
        external_balance=external_balance,
    )


@pytest.fixture
def scenarios(scenario_input: ScenarioGeneratorInput) -> List[Scenario]:
    """Define fixture vectors of all possible scenarios, given the current pre state input."""
    scenarios_list: List[Scenario] = []

    call_combinations = ScenariosCallCombinations(scenario_input).generate()
    for combination in call_combinations:
        scenarios_list.append(combination)

    call_combinations = scenarios_create_combinations(scenario_input)
    for combination in call_combinations:
        scenarios_list.append(combination)

    revert_combinations = scenarios_revert_combinations(scenario_input)
    for combination in revert_combinations:
        scenarios_list.append(combination)

    return scenarios_list


@pytest.mark.valid_from("Frontier")
@pytest.mark.parametrize(
    # select program to debug (program, "scenario_name")
    # program=None select all programs
    # scenario_name="" select all scenarios
    # Example: [ScenarioDebug(test_param=program_invalid, scenario_name="scenario_CALL_CALL")],
    "debug",
    # [ScenarioDebug(test_param=program_invalid, scenario_name="scenario_CALL_CALL")],
    [ScenarioDebug(test_param=None, scenario_name="")],
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
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    expected_result: ProgramResult,
    debug: ScenarioDebug,
    operation: Bytecode,
    scenarios,
):
    """
    Test given operation in different scenarios
    Verify that it's return value equal to expected result on every scenario,
    that is valid for the given fork.

    Note: Don't use pytest parametrize for scenario production, because scenarios will be complex
    Generate one test file for [each operation] * [each scenario] to save space
    As well as operations will be complex too
    """
    tx_env = Environment()
    tx_origin: Address = pre.fund_eoa()

    blocks: List[Block] = []
    post: dict = {}
    for scenario in scenarios:
        if debug.scenario_name and scenario.name != debug.scenario_name:
            continue

        if debug.test_param is not None:
            debug_program = debug.test_param.values[0]
            if hasattr(debug_program, "hex") and operation.hex() != debug_program.hex():
                continue

        post_storage = Storage()
        result_slot = post_storage.store_next(1, hint=f"runner result {scenario.name}")

        tx_max_gas = (
            7_000_000
            if hasattr(program_invalid.values[0], "hex")
            and operation.hex() == program_invalid.values[0].hex()
            else 1_000_000
        )
        tx_gasprice: int = 10
        exec_env = ExecutionEnvironment(
            fork=fork,
            origin=tx_origin,
            gasprice=tx_gasprice,
            timestamp=tx_env.timestamp,  # we can't know timestamp before head, use gas hash
            number=len(blocks) + 1,
            gaslimit=tx_env.gas_limit,
            coinbase=tx_env.fee_recipient,
        )

        def make_result(scenario: Scenario, exec_env: ExecutionEnvironment, post: Storage) -> int:
            """Make Scenario post result."""
            if scenario.halts:
                return post.store_next(0, hint=scenario.name)
            else:
                return post.store_next(
                    translate_result(expected_result, scenario.env, exec_env), hint=scenario.name
                )

        runner_contract = pre.deploy_contract(
            code=Op.MSTORE(0, 0)
            + Op.CALL(tx_max_gas, scenario.code, 0, 0, 0, 0, 32)
            + Op.SSTORE(make_result(scenario, exec_env, post_storage), Op.MLOAD(0))
            + Op.SSTORE(result_slot, 1),
            storage={
                result_slot: 0xFFFF,
            },
        )

        tx = Transaction(
            sender=tx_origin,
            gas_limit=tx_max_gas + 100_000,
            gas_price=tx_gasprice,
            to=runner_contract,
            data=bytes.fromhex("11223344"),
            value=0,
            protected=False,
        )

        post[runner_contract] = Account(storage=post_storage)
        blocks.append(Block(txs=[tx], post=post))

    blockchain_test(
        pre=pre,
        blocks=blocks,
        post=post,
    )
