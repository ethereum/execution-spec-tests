"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_forks import Verkle
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

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "priority_fee",
    [
        0,
        100,
    ],
)
def test_coinbase_fees(blockchain_test: BlockchainTestFiller, priority_fee):
    """
    Test coinbase witness.
    """
    coinbase_addr = Address("0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba")
    env = Environment(
        fee_recipient=coinbase_addr,
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        ty=2,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        value=100,
        gas_limit=1_000_000,
        max_fee_per_gas=1_000,
        max_priority_fee_per_gas=priority_fee,
    )

    # TODO(verkle): change value when filling
    post = {} if priority_fee == 0 else {coinbase_addr: Account(balance=0x42)}

    witness_check = WitnessCheck(fork=Verkle)
    witness_check.add_account_full(address=TestAddress, account=pre[TestAddress])
    witness_check.add_account_full(address=TestAddress2, account=None)
    if priority_fee > 0:
        witness_check.add_account_full(address=coinbase_addr, account=None)

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
