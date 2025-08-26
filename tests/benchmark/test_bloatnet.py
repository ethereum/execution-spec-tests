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

    storage_slot: int = 0

    storage = Storage()

    totalgas = gas_costs.G_BASE * 3 + gas_costs.G_VERY_LOW  # Initial gas for PUSH0 + CALLDATALOAD + DUP1 + POP (at the end)
    gas_increment = gas_costs.G_VERY_LOW * 2 + gas_costs.G_STORAGE_SET + gas_costs.G_COLD_SLOAD
    sstore_code = Op.PUSH0 + Op.CALLDATALOAD + Op.DUP1
    i = 0
    while totalgas + gas_increment < Environment().gas_limit:
        totalgas += gas_increment
        sstore_code = sstore_code + Op.SSTORE(i, Op.DUP4)

        storage[storage_slot] = final_storage_value
        storage_slot += 1
        i += 1
    sstore_code = sstore_code + Op.POP  # Drop last value on the stack

    sender = pre.fund_eoa()
    print(sender)
    contract_address = pre.deploy_contract(
        code=sstore_code,
        storage=storage,
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
