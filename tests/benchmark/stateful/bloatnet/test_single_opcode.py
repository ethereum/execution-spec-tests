"""
abstract: BloatNet single-opcode benchmark cases for state-related operations.

   These tests focus on individual EVM opcodes (SLOAD, SSTORE) to measure
   their performance when accessing many storage slots across pre-deployed
   contracts. Unlike multi-opcode tests, these isolate single operations
   to benchmark specific state-handling bottlenecks.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
    While,
)
from ethereum_test_vm import Bytecode
from ethereum_test_vm import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/bloatnet.md"
REFERENCE_SPEC_VERSION = "1.0"

# ERC20 function selectors
BALANCEOF_SELECTOR = 0x70A08231  # balanceOf(address)
APPROVE_SELECTOR = 0x095EA7B3  # approve(address,uint256)
ALLOWANCE_SELECTOR = 0xDD62ED3E  # allowance(address,address)


# SLOAD BENCHMARK ARCHITECTURE:
#
#   [Pre-deployed ERC20 Contract] ──── Storage slots for balances
#           │
#           │  balanceOf(address) → SLOAD(keccak256(address || slot))
#           │
#   [Attack Contract] ──CALL──► ERC20.balanceOf(random_address)
#           │
#           └─► Loop(i=0 to N):
#                 1. Generate random address from counter
#                 2. CALL balanceOf(random_address) → forces cold SLOAD
#                 3. Most addresses have zero balance → empty storage slots
#
# WHY IT STRESSES CLIENTS:
#   - Each balanceOf() call forces a cold SLOAD on a likely-empty slot
#   - Storage slot = keccak256(address || balances_slot)
#   - Random addresses ensure maximum cache misses
#   - Tests client's sparse storage handling efficiency


@pytest.mark.valid_from("Prague")
def test_sload_empty_erc20_balanceof(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    address_stubs,
):
    """
    BloatNet SLOAD benchmark using ERC20 balanceOf queries on random addresses.

    This test:
    1. Auto-discovers ERC20 contracts from stubs (pattern: erc20_contract_*)
    2. Splits gas budget evenly across all discovered contracts
    3. Queries balanceOf() incrementally starting by 0 and increasing by 1.
    (thus forcing SLOADs to non-existing addresses.)
    """
    gas_costs = fork.gas_costs()

    # Calculate gas costs
    intrinsic_gas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # Cost per iteration (attack contract overhead + balanceOf call)
    cost_per_iteration = (
        # Attack contract loop overhead
        gas_costs.G_VERY_LOW * 2  # MLOAD counter (3*2)
        + gas_costs.G_VERY_LOW * 2  # MSTORE selector (3*2)
        + gas_costs.G_VERY_LOW * 3  # MLOAD + MSTORE address (3*3)
        + gas_costs.G_BASE  # POP (2)
        + gas_costs.G_BASE * 3  # SUB + MLOAD + MSTORE for counter decrement (2*3)
        + gas_costs.G_BASE * 2  # ISZERO * 2 for loop condition (2*2)
        + gas_costs.G_MID  # JUMPI (8)
        # CALL to ERC20 contract
        + gas_costs.G_WARM_ACCOUNT_ACCESS  # Warm CALL to same contract (100)
        # Inside ERC20 balanceOf
        + gas_costs.G_VERY_LOW  # PUSH4 selector (3)
        + gas_costs.G_BASE  # EQ selector match (2)
        + gas_costs.G_MID  # JUMPI to function (8)
        + gas_costs.G_JUMPDEST  # JUMPDEST at function start (1)
        + gas_costs.G_VERY_LOW * 2  # CALLDATALOAD arg (3*2)
        + gas_costs.G_KECCAK_256  # keccak256 static (30)
        + gas_costs.G_KECCAK_256_WORD * 2  # keccak256 dynamic for 64 bytes (2*6)
        + gas_costs.G_COLD_SLOAD  # Cold SLOAD (2100)
        + gas_costs.G_VERY_LOW * 3  # MSTORE result + RETURN setup (3*3)
        # RETURN costs 0 gas
    )

    num_contracts = len(address_stubs.root)

    # Calculate gas budget per contract and calls per contract
    available_gas = gas_benchmark_value - intrinsic_gas
    gas_per_contract = available_gas // num_contracts
    calls_per_contract = int(gas_per_contract // cost_per_iteration)

    # Deploy all discovered ERC20 contracts using stubs
    # In execute mode: stubs point to already-deployed contracts on chain
    # In fill mode: empty bytecode is deployed as placeholder
    erc20_addresses = []
    for stub_name in address_stubs.root:
        addr = pre.deploy_contract(
            code=Bytecode(),  # Required parameter, ignored for stubs in execute mode
            stub=stub_name,
        )
        erc20_addresses.append(addr)

    # Log test requirements
    print(
        f"Total gas budget: {gas_benchmark_value / 1_000_000:.1f}M gas. "
        f"~{gas_per_contract / 1_000_000:.1f}M gas per contract, "
        f"{calls_per_contract} balanceOf calls per contract."
    )

    # Build attack code that loops through each contract
    attack_code: Bytecode = Op.JUMPDEST  # Entry point

    for erc20_address in erc20_addresses:
        # For each contract, initialize counter and loop
        attack_code += (
            # Initialize counter in memory[0] = number of calls
            Op.MSTORE(offset=0, value=calls_per_contract)
            # Loop for this specific contract
            + While(
                condition=Op.MLOAD(0) + Op.ISZERO + Op.ISZERO,  # Continue while counter > 0
                body=(
                    # Use counter directly as address (cheapest option)
                    # Store function selector at memory[32]
                    Op.MSTORE(offset=32, value=BALANCEOF_SELECTOR)
                    # Store address at memory[64] (just use counter as address)
                    + Op.MSTORE(offset=64, value=Op.MLOAD(0))
                    # Call balanceOf(address) on ERC20 contract
                    + Op.CALL(
                        address=erc20_address,
                        value=0,
                        args_offset=32,
                        args_size=36,
                        ret_offset=96,
                        ret_size=32,
                    )
                    + Op.POP  # Discard result
                    # Decrement counter: counter - 1
                    + Op.MSTORE(offset=0, value=Op.SUB(Op.MLOAD(0), 1))
                ),
            )
        )

    # Deploy attack contract
    attack_address = pre.deploy_contract(code=attack_code)

    # Run the attack
    attack_tx = Transaction(
        to=attack_address,
        gas_limit=gas_benchmark_value,
        sender=pre.fund_eoa(),
    )

    # Post-state
    post = {
        attack_address: Account(storage={}),
    }

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[attack_tx])],
        post=post,
    )
