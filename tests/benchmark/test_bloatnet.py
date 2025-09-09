"""
abstract: Tests that benchmarks EVMs to estimate the costs of  stateful opcodes.
    Tests that benchmarks EVMs to estimate the costs of stateful opcodes..
"""

import pytest

from ethereum_test_base_types import HashInt
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Storage,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_vm import Bytecode


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("storage_value", [0x01 << 248, 0x01])
def test_bloatnet_sstore_0_to_1(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    storage_value: int,
):
    """
    Benchmark test that maximizes SSTORE operations (0 -> 1) by filling
    a block with multiple transactions, with each one containing a contract
    that performs a set of SSTOREs.

    The test iteratively creates new transactions until the cumulative gas used
    reaches the block's gas benchmark value. Each transaction deploys a contract
    that performs as many SSTOREs as possible within the transaction's gas limit.
    """
    gas_costs = fork.gas_costs()
    intrinsic_gas_calc = fork.transaction_intrinsic_cost_calculator()

    tx_gas_cap = fork.transaction_gas_limit_cap() or gas_benchmark_value

    calldata = storage_value.to_bytes(32, "big").rstrip(b"\x00")

    total_sstores = 0
    total_block_gas_used = 0
    all_txs = []

    expected_storage_state = {}

    while total_block_gas_used <= gas_benchmark_value:
        remaining_block_gas = gas_benchmark_value - total_block_gas_used
        tx_gas_limit = min(remaining_block_gas, tx_gas_cap)

        intrinsic_gas_with_data_floor = intrinsic_gas_calc(calldata=calldata)
        if tx_gas_limit <= intrinsic_gas_with_data_floor:
            break

        opcode_gas_budget = tx_gas_limit - intrinsic_gas_with_data_floor

        # Setup code to load value from calldata
        tx_contract_code = Op.PUSH0 + Op.CALLDATALOAD
        tx_opcode_gas = gas_costs.G_BASE + gas_costs.G_VERY_LOW  # PUSH0 + CALLDATALOAD

        sstore_per_op_cost = (
            gas_costs.G_VERY_LOW * 2  # PUSH + DUP1
            + gas_costs.G_COLD_SLOAD
            + gas_costs.G_STORAGE_SET  # SSTORE
        )

        tx_sstores_count = (opcode_gas_budget - tx_opcode_gas) // sstore_per_op_cost

        # If no SSTOREs could be added, we've filled the block
        if tx_sstores_count == 0:
            break

        tx_opcode_gas += sstore_per_op_cost * tx_sstores_count
        for slot in range(total_sstores, total_sstores + tx_sstores_count):
            tx_contract_code += Op.SSTORE(slot, Op.DUP1)

        contract_address = pre.deploy_contract(code=tx_contract_code)
        tx = Transaction(
            to=contract_address,
            gas_limit=tx_gas_limit,
            data=calldata,
            sender=pre.fund_eoa(),
        )
        all_txs.append(tx)

        actual_intrinsic_consumed = intrinsic_gas_calc(
            calldata=calldata,
            # The actual gas consumed uses the standard intrinsic cost
            # (prior execution), not the floor cost used for validation
            return_cost_deducted_prior_execution=True,
        )

        tx_gas_used = actual_intrinsic_consumed + tx_opcode_gas
        total_block_gas_used += tx_gas_used

        # update expected storage state for each contract
        expected_storage_state[contract_address] = Account(
            storage=Storage(
                {
                    HashInt(slot): HashInt(storage_value)
                    for slot in range(total_sstores, total_sstores + tx_sstores_count)
                }
            )
        )

        total_sstores += tx_sstores_count

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=all_txs)],
        post=expected_storage_state,
        expected_benchmark_gas_used=total_block_gas_used,
    )


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("final_storage_value", [0x02 << 248, 0x02])
def test_bloatnet_sstore_1_to_2(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_benchmark_value: int,
    final_storage_value: int,
):
    """
    Benchmark test that maximizes SSTORE operations (1 -> 2).

    This test pre-fills storage slots with value=1, then overwrites them with value=2.
    This represents the case of changing a non-zero value to a different non-zero value,
    """
    gas_costs = fork.gas_costs()
    intrinsic_gas_calc = fork.transaction_intrinsic_cost_calculator()
    tx_gas_cap = fork.transaction_gas_limit_cap() or gas_benchmark_value

    initial_value = final_storage_value // 2
    calldata = final_storage_value.to_bytes(32, "big").rstrip(b"\x00")

    total_sstores = 0
    total_block_gas_used = 0
    all_txs = []
    expected_storage_state = {}

    while total_block_gas_used <= gas_benchmark_value:
        remaining_block_gas = gas_benchmark_value - total_block_gas_used
        tx_gas_limit = min(remaining_block_gas, tx_gas_cap)

        intrinsic_gas_with_data_floor = intrinsic_gas_calc(calldata=calldata)
        if tx_gas_limit <= intrinsic_gas_with_data_floor:
            break

        opcode_gas_budget = tx_gas_limit - intrinsic_gas_with_data_floor

        # Setup code to load value from calldata
        tx_contract_code = Op.PUSH0 + Op.CALLDATALOAD
        tx_opcode_gas = gas_costs.G_BASE + gas_costs.G_VERY_LOW  # PUSH0 + CALLDATALOAD

        sstore_per_op_cost = (
            gas_costs.G_VERY_LOW * 2  # PUSH + DUP1
            + gas_costs.G_COLD_SLOAD
            + gas_costs.G_STORAGE_RESET  # SSTORE
        )

        tx_sstores_count = (opcode_gas_budget - tx_opcode_gas) // sstore_per_op_cost

        if tx_sstores_count == 0:
            break

        tx_opcode_gas += sstore_per_op_cost * tx_sstores_count
        for slot in range(total_sstores, total_sstores + tx_sstores_count):
            tx_contract_code += Op.SSTORE(slot, Op.DUP1)

        # Pre-fill storage with initial values
        initial_storage = {
            slot: initial_value for slot in range(total_sstores, total_sstores + tx_sstores_count)
        }

        contract_address = pre.deploy_contract(
            code=tx_contract_code,
            storage=initial_storage,  # type: ignore
        )
        tx = Transaction(
            to=contract_address,
            gas_limit=tx_gas_limit,
            data=calldata,
            sender=pre.fund_eoa(),
        )
        all_txs.append(tx)

        actual_intrinsic_consumed = intrinsic_gas_calc(
            calldata=calldata, return_cost_deducted_prior_execution=True
        )

        tx_gas_used = actual_intrinsic_consumed + tx_opcode_gas
        total_block_gas_used += tx_gas_used

        expected_storage_state[contract_address] = Account(
            storage=Storage(
                {
                    HashInt(slot): HashInt(final_storage_value)
                    for slot in range(total_sstores, total_sstores + tx_sstores_count)
                }
            )
        )

        total_sstores += tx_sstores_count

    blockchain_test(
        pre=pre,
        blocks=[Block(txs=all_txs)],
        post=expected_storage_state,
        expected_benchmark_gas_used=total_block_gas_used,
    )


# Warm reads are very cheap, which means you can really fill a block
# with them. Only fill the block by a factor of SPEEDUP.
SPEEDUP: int = 100


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_warm(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """Test that loads warm storage locations many times."""
    gas_costs = fork.gas_costs()
    intrinsic_gas_calc = fork.transaction_intrinsic_cost_calculator()
    tx_gas_cap = fork.transaction_gas_limit_cap() or gas_benchmark_value

    # Pre-fill storage with values
    num_slots = 100  # Number of storage slots to warm up
    storage = Storage({HashInt(i): HashInt(0xDEADBEEF + i) for i in range(num_slots)})

    # Gas costs for operations
    # PUSH + SLOAD + POP for cold access
    cold_sload_cost = gas_costs.G_VERY_LOW + gas_costs.G_COLD_SLOAD + gas_costs.G_BASE
    # PUSH + SLOAD + POP for warm access
    warm_sload_cost = gas_costs.G_VERY_LOW + gas_costs.G_WARM_SLOAD + gas_costs.G_BASE

    # Calculate how many operations fit in a single transaction
    intrinsic_gas = intrinsic_gas_calc(calldata=b"")
    opcode_gas_budget = tx_gas_cap - intrinsic_gas

    # Calculate max warm loads that can fit in a transaction
    # (applying SPEEDUP factor to reduce the number of operations)
    num_warm_loads_per_tx = opcode_gas_budget // (SPEEDUP * warm_sload_cost)

    # Build the code that does warm loads
    # Since storage slots are already warmed within each transaction,
    # we just need to access them repeatedly
sload_code = Bytecode()
sload_code += sum(Op.POP(Op.SLOAD(i)) for i in range(num_slots))
sload_code += sum(Op.POP(Op.SLOAD(i % num_slots)) for i in range(num_warm_loads_per_tx))

    # Deploy the contract once
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    total_block_gas_used = 0
    all_txs = []

    # Create multiple transactions until we reach gas benchmark
    while total_block_gas_used < gas_benchmark_value:
        remaining_block_gas = gas_benchmark_value - total_block_gas_used
        if remaining_block_gas < intrinsic_gas:
            break

        tx_gas_limit = min(remaining_block_gas, tx_gas_cap)

        # Calculate actual operations that will execute
        actual_opcode_budget = tx_gas_limit - intrinsic_gas

        # Check if we can at least warm up the slots
        warmup_gas = num_slots * cold_sload_cost
        if actual_opcode_budget < warmup_gas:
            break

        # Calculate how many warm loads we can actually do
        remaining_budget = actual_opcode_budget - warmup_gas
        actual_warm_loads = min(num_warm_loads_per_tx, remaining_budget // warm_sload_cost)

        tx = Transaction(
            to=contract_address,
            gas_limit=tx_gas_limit,
            sender=pre.fund_eoa(),
        )
        all_txs.append(tx)

        tx_gas_used = intrinsic_gas + warmup_gas + (actual_warm_loads * warm_sload_cost)
        total_block_gas_used += tx_gas_used

    post = {contract_address: Account(storage=storage)}
    blockchain_test(
        pre=pre,
        blocks=[Block(txs=all_txs)],
        post=post,
        expected_benchmark_gas_used=total_block_gas_used,
    )


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_cold(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, gas_benchmark_value: int
):
    """Test that loads many different cold storage locations."""
    gas_costs = fork.gas_costs()
    intrinsic_gas_calc = fork.transaction_intrinsic_cost_calculator()
    tx_gas_cap = fork.transaction_gas_limit_cap() or gas_benchmark_value

    # PUSH + Cold SLOAD + POP
    cold_sload_cost = gas_costs.G_VERY_LOW + gas_costs.G_COLD_SLOAD + gas_costs.G_BASE

    # Calculate max slots that fit in a single transaction
    intrinsic_gas = intrinsic_gas_calc()
    opcode_gas_budget = tx_gas_cap - intrinsic_gas
    max_slots_per_tx = opcode_gas_budget // cold_sload_cost

    # Calculate total slots needed to fill the benchmark
    total_max_slots = gas_benchmark_value // cold_sload_cost

    # Build storage for all slots we'll potentially access
    storage = Storage({HashInt(i): HashInt(0xC0FFEE + i) for i in range(total_max_slots)})

    # Build code that loads max_slots_per_tx cold slots
    sload_code = sum(Op.POP(Op.SLOAD(i)) for i in range(max_slots_per_tx))

    # Deploy the contract once
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    total_block_gas_used = 0
    all_txs = []

    # Create multiple transactions until we reach gas benchmark
    while total_block_gas_used < gas_benchmark_value:
        remaining_block_gas = gas_benchmark_value - total_block_gas_used
        if remaining_block_gas < intrinsic_gas:
            break

        tx_gas_limit = min(remaining_block_gas, tx_gas_cap)

        # Calculate actual slots that will fit
        actual_opcode_budget = tx_gas_limit - intrinsic_gas
        actual_slots = min(max_slots_per_tx, actual_opcode_budget // cold_sload_cost)

        if actual_slots == 0:
            break

        tx = Transaction(
            to=contract_address,
            gas_limit=tx_gas_limit,
            sender=pre.fund_eoa(),
        )
        all_txs.append(tx)

        tx_gas_used = intrinsic_gas + (actual_slots * cold_sload_cost)
        if actual_slots < max_slots_per_tx:
            total_block_gas_used += tx_gas_limit
        else:
            total_block_gas_used += tx_gas_used

    post = {contract_address: Account(storage=storage)}
    blockchain_test(
        pre=pre,
        blocks=[Block(txs=all_txs)],
        post=post,
        expected_benchmark_gas_used=total_block_gas_used,
    )
