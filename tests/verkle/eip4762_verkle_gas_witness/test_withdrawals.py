"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Withdrawal,
)

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
def test_withdrawals(blockchain_test: BlockchainTestFiller, fork: str):
    """
    Test withdrawals witness.
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
    }

    blocks = [
        Block(
            txs=[],
            withdrawals=[
                Withdrawal(index=0, validator_index=0, amount=3, address=TestAddress),
                Withdrawal(index=1, validator_index=1, amount=4, address=TestAddress2),
            ],
        )
    ]

    post = {
        TestAddress: Account(balance=1000000000003000000000),
        TestAddress2: Account(balance=4000000000),
    }

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.add_account_full(TestAddress2, pre[TestAddress2])

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        witness=witness,
    )
