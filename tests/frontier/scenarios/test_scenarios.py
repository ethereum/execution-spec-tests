"""
Call every possible opcode and test that the subcall is successful
if the opcode is supported by the fork and fails otherwise.
"""

from typing import Dict, List

import pytest

from ethereum_test_base_types import to_bytes
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .common import (
    ProgramResult,
    Scenario,
    ScenarioEnvironment,
    ScenarioExpectOpcode,
    ScenarioGeneratorInput,
)
from .programs.all_frontier_opcodes import program_all_frontier_opcodes
from .programs.context_calls import (
    program_address,
    program_balance,
    program_caller,
    program_callvalue,
    program_chainid,
    program_codecopy_codesize,
    program_origin,
    program_selfbalance,
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
    balance_code = "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff31"
    if balance_code in operation.hex():
        new_operation_hex = operation.hex().replace(
            balance_code,
            (Op.BALANCE(external_address)).hex(),
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


def translate_result(
    fork: Fork, res: ProgramResult, env: ScenarioEnvironment, origin: Address
) -> int:
    """Translate expected program result into concrete value, given the scenario evm environment"""
    if fork < res.from_fork:
        return 0
    if isinstance(res.result, ScenarioExpectOpcode):
        if res.result == ScenarioExpectOpcode.TX_ORIGIN:
            return int(origin.hex(), 16)
        if res.result == ScenarioExpectOpcode.CODE_ADDRESS:
            return int(env.code_address.hex(), 16)
        if res.result == ScenarioExpectOpcode.CODE_CALLER:
            return int(env.code_caller.hex(), 16)
        if res.result == ScenarioExpectOpcode.SELFBALANCE:
            return int(env.selfbalance)
        if res.result == ScenarioExpectOpcode.BALANCE:
            return int(env.ext_balance)
        if res.result == ScenarioExpectOpcode.CALL_VALUE:
            return int(env.call_value)

    return res.result


@pytest.mark.valid_from("Frontier")
@pytest.mark.parametrize(
    "operation, result",
    [
        program_callvalue,
        program_balance,
        program_selfbalance,
        program_chainid,
        program_codecopy_codesize,
        program_origin,
        program_caller,
        program_address,
        program_all_frontier_opcodes,
    ],
)
def test_scenarios(
    state_test: StateTestFiller,
    pre: Alloc,
    fork: Fork,
    result: ProgramResult,
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
    tx_origin: Address = pre.fund_eoa()
    code_worked = 1000

    runner_contract = pre.deploy_contract(
        code=sum(
            Op.MSTORE(0, 0)
            # MAYBE NEED TO PASS our address by Op.Address as the input value to scenario.code
            # so it can verify the Op.CALLER for delegate call contexts
            + Op.CALL(1000000, scenario.code, 0, 0, 0, 0, 32) + Op.SSTORE(index, Op.MLOAD(0))
            for index, (scenario) in enumerate(scenarios)
        )
        + Op.SSTORE(code_worked, 1)
    )
    post = {
        runner_contract: Account(
            storage={
                **{
                    index: translate_result(fork, result, scenario.env, tx_origin)
                    if not scenario.reverting
                    else 0
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
        gas_price=10,
        to=runner_contract,
        data=b"",
        value=0,
        protected=False,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx, post_hint=hint)
