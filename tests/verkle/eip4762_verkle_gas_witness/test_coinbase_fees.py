"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
)

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize("priority_fee", [0, 100])
def test_coinbase_fees(blockchain_test: BlockchainTestFiller, fork: str, priority_fee):
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
        gas_price=priority_fee,
    )
    blocks = [Block(txs=[tx])]

    # TODO(verkle): change value when filling
    post = {} if priority_fee == 0 else {coinbase_addr: Account(balance=0x42)}

    witness = Witness()
    witness.add_account_full(coinbase_addr, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.add_account_full(TestAddress2, pre[TestAddress2])

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        witness=witness,
    )
