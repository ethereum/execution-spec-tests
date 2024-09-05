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
    WitnessCheck,
)

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

    post = {
        TestAddress: Account(balance=1000000000003000000000),
        TestAddress2: Account(balance=4000000000),
    }

    witness_check = WitnessCheck()
    for address in [TestAddress, TestAddress2]:
        witness_check.add_account_full(
            address=address,
            account=pre.get(address),
        )

    blocks = [
        Block(
            txs=[],
            withdrawals=[
                Withdrawal(index=0, validator_index=0, amount=3, address=TestAddress),
                Withdrawal(index=1, validator_index=1, amount=4, address=TestAddress2),
            ],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
