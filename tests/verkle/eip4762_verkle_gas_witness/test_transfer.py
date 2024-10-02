"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Fork, Verkle
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_types.verkle.helpers import chunkify_code

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

EmptyAddress = Address("0xffff5374fce5edbc8e2a8697c15331677e6ebfff")
precompile_address = Address("0x04")
system_contract_address = Address("0xfffffffffffffffffffffffffffffffffffffffe")


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "target",
    [
        TestAddress2,
        EmptyAddress,
        precompile_address,
        system_contract_address,
    ],
)
@pytest.mark.parametrize(
    "value",
    [0, 1],
)
def test_transfer(blockchain_test: BlockchainTestFiller, fork: Fork, target, value):
    """
    Test that value transfer generates a correct witness.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(balance=2000000000000000000000),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=target,
        gas_limit=100000000,
        gas_price=10,
        value=value,
    )

    post_account = pre.get(target, Account())
    if post_account is None:
        post_account = Account()
    post_account.balance += value
    post = {
        target: post_account,
    }

    witness_check = WitnessCheck(fork=Verkle)
    witness_check.add_account_full(env.fee_recipient, None)
    witness_check.add_account_full(TestAddress, pre[TestAddress])
    if target == system_contract_address:
        pre_allocations = fork.pre_allocation_blockchain()
        witness_check.add_account_full(
            Address(target), Account(**pre_allocations.get(Address(target)))
        )
    else:
        witness_check.add_account_full(target, pre.get(target))

    if target == system_contract_address:
        code = Account(**fork.pre_allocation_blockchain()[system_contract_address]).code
        code_chunks = chunkify_code(code)
        for i, code_chunk in enumerate(code_chunks, start=0):
            witness_check.add_code_chunk(
                address=system_contract_address, chunk_number=i, value=code_chunk
            )

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
