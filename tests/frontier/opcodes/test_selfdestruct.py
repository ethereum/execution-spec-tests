"""
Test the SELFDESTRUCT opcode.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    Initcode,
    TestAddress,
    Transaction,
    compute_create_address,
)

@pytest.mark.valid_from("Frontier")
@pytest.mark.valid_until("Homestead")
def test_double_kill(blockchain_test: BlockchainTestFiller, fork: Fork):
    """
    Test that when two transactions attempt to destruct a contract,
    the second transaction actually resurrects the contract as an empty account (prior to Spurious Dragon).
    """

    env = Environment()
    pre = {
        TestAddress: Account(
            balance=1000000000000000000000
        ),
    }

    deploy_code=(Op.SELFDESTRUCT(Op.ADDRESS))

    initcode = Initcode(deploy_code=deploy_code).bytecode

    create_tx = Transaction(
        nonce=0,
        gas_limit=100000000,
        protected=False,
        to=None,
        data=initcode,
    )

    created_contract_address = compute_create_address(address=TestAddress, nonce=0)

    block1 = Block(txs=[create_tx])

    first_kill = Transaction(
        nonce=1,
        gas_limit=100000000,
        protected=False,
        to=created_contract_address,
    )

    second_kill = Transaction(
        nonce=2,
        gas_limit=100000000,
        protected=False,
        to=created_contract_address,
    )

    block2 = Block(txs=[first_kill, second_kill])
    
    post = {
        created_contract_address: Account(
            nonce=0,
            balance=0,
            code=None,
            storage={},
        ),
    }

    blockchain_test(genesis_environment=env, pre=pre, post=post, blocks=[block1, block2])
