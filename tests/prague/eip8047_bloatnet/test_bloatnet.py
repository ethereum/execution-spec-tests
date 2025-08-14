"""
abstract: Tests [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)
    Test cases for [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)].
"""

import pytest

from ethereum_test_tools import Account, Alloc, Block, BlockchainTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_forks import Fork

REFERENCE_SPEC_GIT_PATH = "DUMMY/eip-DUMMY.md"
REFERENCE_SPEC_VERSION = "DUMMY_VERSION"


@pytest.mark.valid_from("Prague")
def test_bloatnet(blockchain_test: BlockchainTestFiller, pre: Alloc, fork: Fork):
    """
    A test that calls a contract with many SSTOREs

    The first block will have many SSTORES that go from 0 -> 1
    and the 2nd block will have many SSTORES that go from 1 -> 2
    """
    # Get gas costs for the current fork
    gas_costs = fork.gas_costs()

    storage_slot: int = 0

    storage = {}
    GasLimit = 30_000_000   # Default gas limit seems to be >90M in this env

    totalgas = gas_costs.G_BASE * 2  # Initial gas for PUSH0 + CALLDATALOAD
    gas_increment  = gas_costs.G_VERY_LOW * 2 + gas_costs.G_STORAGE_SET + gas_costs.G_COLD_SLOAD
    sstore_code = Op.PUSH0 + Op.CALLDATALOAD + Op.DUP1
    i = 0
    while totalgas + gas_increment < GasLimit:
        totalgas += gas_increment
        # print(f"increment={gas_increment} < totalgas={totalgas} i={i}")
        sstore_code = sstore_code + Op.DUP1
        if i < 256:
            sstore_code = sstore_code + Op.PUSH1(i)
        else:
            sstore_code = sstore_code + Op.PUSH2(i)
        
        sstore_code = sstore_code + Op.SSTORE(unchecked=True)
        
        storage[storage_slot] = 0x02 << 248
        storage_slot += 1
        i += 1
    sstore_code = sstore_code + Op.POP # Drop last value on the stack

    sender = pre.fund_eoa()
    print(sender)
    contract_address = pre.deploy_contract(
        code=sstore_code,
        storage=storage,
    )

    tx_0_1 = Transaction(
        to=contract_address,
        gas_limit=GasLimit,
        data=b'\x01',  # Single byte 0x01
        value=0,
        sender=sender,
    )
    tx_1_2 = Transaction(
        to=contract_address,
        gas_limit=30000000,
        data=b'\x02',  # Single byte 0x02, turns into 0x2000000000000000000000000000000000000000000000000000000000000000
        value=0,
        sender=sender,
    )

    post = {contract_address: Account(storage=storage)}

    blockchain_test(pre=pre, blocks=[Block(txs=[tx_0_1, tx_1_2])], post=post)
