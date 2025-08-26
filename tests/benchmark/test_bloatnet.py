"""
abstract: Tests [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)
    Test cases for [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)].
"""

import pytest

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

REFERENCE_SPEC_GIT_PATH = "DUMMY/eip-DUMMY.md"
REFERENCE_SPEC_VERSION = "0.1"


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

    totalgas = gas_costs.G_BASE * 2 + gas_costs.G_VERY_LOW # Initial gas for PUSH0 + CALLDATALOAD + POP (at the end)
    totalgas = totalgas + fork.transaction_intrinsic_cost_calculator()(calldata=data);
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
