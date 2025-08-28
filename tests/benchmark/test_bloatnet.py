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
    Environment,
    Storage,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("final_storage_value", [0x02 << 248, 0x02])
def test_bloatnet(
    blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork, final_storage_value: int
):
    """
    A test that calls a contract with many SSTOREs.

    The first block will have many SSTORES that go from 0 -> 1
    and the 2nd block will have many SSTORES that go from 1 -> 2
    """
    # Get gas costs for the current fork
    gas_costs = fork.gas_costs()

    # this is only used for computing the intinsic gas
    data = final_storage_value.to_bytes(32, "big").rstrip(b"\x00")

    storage = Storage()

    # Initial gas for PUSH0 + CALLDATALOAD + POP (at the end)
    totalgas = gas_costs.G_BASE * 2 + gas_costs.G_VERY_LOW
    totalgas = totalgas + fork.transaction_intrinsic_cost_calculator()(calldata=data)
    gas_increment = gas_costs.G_VERY_LOW * 2 + gas_costs.G_STORAGE_SET + gas_costs.G_COLD_SLOAD
    sstore_code = Op.PUSH0 + Op.CALLDATALOAD
    storage_slot: int = 0
    while totalgas + gas_increment < Environment().gas_limit:
        totalgas += gas_increment
        sstore_code = sstore_code + Op.SSTORE(storage_slot, Op.DUP1)
        storage[storage_slot] = final_storage_value
        storage_slot += 1

    sstore_code = sstore_code + Op.POP  # Drop last value on the stack

    sender = pre.fund_eoa()
    print(sender)
    contract_address = pre.deploy_contract(
        code=sstore_code,
        storage=Storage(),
    )

    tx_0_1 = Transaction(
        to=contract_address,
        gas_limit=Environment().gas_limit,
        data=(final_storage_value // 2).to_bytes(32, "big").rstrip(b"\x00"),
        value=0,
        sender=sender,
    )
    tx_1_2 = Transaction(
        to=contract_address,
        gas_limit=Environment().gas_limit,
        data=final_storage_value.to_bytes(32, "big").rstrip(b"\x00"),
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}

    blockchain_test(pre=pre, blocks=[Block(txs=[tx_0_1, tx_1_2])], post=post)


# Warm reads are very cheap, which means you can really fill a block
# with them. Only fill the block by a factor of SPEEDUP.
SPEEDUP: int = 100


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_warm(blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork):
    """Test that loads warm storage locations many times."""
    gas_costs = fork.gas_costs()

    # Pre-fill storage with values
    num_slots = 100  # Number of storage slots to warm up
    storage = Storage({HashInt(i): HashInt(0xDEADBEEF + i) for i in range(num_slots)})

    # Calculate gas costs
    totalgas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")

    # First pass - warm up all slots (cold access)
    warmup_gas = num_slots * (gas_costs.G_COLD_SLOAD + gas_costs.G_BASE)
    totalgas += warmup_gas

    # Calculate how many warm loads we can fit
    gas_increment = gas_costs.G_WARM_SLOAD + gas_costs.G_BASE  # Warm SLOAD + POP
    remaining_gas = Environment().gas_limit - totalgas
    num_warm_loads = remaining_gas // (SPEEDUP * gas_increment)

    # Build the complete code: warmup + repeated warm loads
    sload_code = Op.SLOAD(0) + Op.POP if num_slots > 0 else Op.STOP
    for i in range(1, num_slots):
        sload_code = sload_code + Op.SLOAD(i) + Op.POP
    for i in range(num_warm_loads):
        sload_code = sload_code + Op.SLOAD(i % num_slots) + Op.POP

    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    tx = Transaction(
        to=contract_address,
        gas_limit=Environment().gas_limit,
        data=b"",
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}
    blockchain_test(pre=pre, blocks=[Block(txs=[tx])], post=post)


@pytest.mark.valid_from("Prague")
def test_bloatnet_sload_cold(blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork):
    """Test that loads many different cold storage locations."""
    gas_costs = fork.gas_costs()

    # Calculate gas costs and max slots
    totalgas = fork.transaction_intrinsic_cost_calculator()(calldata=b"")
    # PUSH + Cold SLOAD + POP
    gas_increment = gas_costs.G_VERY_LOW + gas_costs.G_COLD_SLOAD + gas_costs.G_BASE
    max_slots = (Environment().gas_limit - totalgas) // gas_increment

    # Build storage and code for all slots
    storage = Storage({HashInt(i): HashInt(0xC0FFEE + i) for i in range(max_slots)})
    sload_code = Op.SLOAD(0) + Op.POP if max_slots > 0 else Op.STOP
    for i in range(1, max_slots):
        sload_code = sload_code + Op.SLOAD(i) + Op.POP

    sender = pre.fund_eoa()
    contract_address = pre.deploy_contract(
        code=sload_code,
        storage=storage,
    )

    tx = Transaction(
        to=contract_address,
        gas_limit=Environment().gas_limit,
        data=b"",
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}
    blockchain_test(pre=pre, blocks=[Block(txs=[tx])], post=post)
