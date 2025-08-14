"""
abstract: Tests [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)
    Test cases for [EIP-8047 BloatNet](https://eips.ethereum.org/EIPS/eip-8047)].
"""

import pytest

from ethereum_test_tools import Account, Alloc, Block, BlockchainTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "DUMMY/eip-DUMMY.md"
REFERENCE_SPEC_VERSION = "DUMMY_VERSION"


@pytest.mark.valid_from("Prague")
def test_bloatnet(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    A test that calls a contract with many SSTOREs

    The first block will have many SSTORES that go from 0 -> 1
    and the 2nd block will have many SSTORES that go from 1 -> 2
    """
    # One gotcha is ensuring that the transaction `gas_limit` is set high
    # enough to cover the gas cost of the contract execution.

    storage_slot: int = 1

    sstore_code = Op.PUSH0
    for _ in range(100000):
        sstore_code = sstore_code + Op.SSTORE(storage_slot, 1) # NOTE: this will probably push some value on the stack, but I want to increase it to reduce the amount of gas and the size of the bytecode
        storage_slot += 1
    sstore_code = Op.POP

    sender = pre.fund_eoa()
    print(sender)
    contract_address = pre.deploy_contract(
        code=sstore_code,
        storage={},
    )

    tx_0_1 = Transaction(
        to=contract_address,
        gas_limit=30000000,
        data=b"",
        value=0,
        sender=sender,
    )
    tx_1_2 = Transaction(
        to=contract_address,
        gas_limit=30000000,
        data=b"",
        value=0,
        sender=sender,
    )

    # TODO: Modify post-state allocations here.
    post = {contract_address: Account(storage={storage_slot: 0x2})}

    blockchain_test(pre=pre, blocks=[Block(txs=[tx_0_1]), Block(txs=[tx_1_2])], post=post)
