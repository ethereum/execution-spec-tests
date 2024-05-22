"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

from typing import Dict

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

from ..temp_verkle_helpers import AccountHeaderEntry, vkt_key_header

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x09")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "target, value, sender_balance",
    [
        (TestAddress2, 0, 1_000_000),
        (TestAddress2, 1, 1_000_000),
        (precompile_address, 0, 1_000_000),
        (precompile_address, 1, 1_000_000),
        (TestAddress2, 1, 0),  # failing tx
        precompile_address,
    ],
)
def test_transfer(blockchain_test: BlockchainTestFiller, fork: str, target, value, sender_balance):
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
        TestAddress: Account(balance=sender_balance),
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
    blocks = [Block(txs=[tx])]

    witness_keys: Dict[str, int | bytes] = {}
    witness_keys[vkt_key_header(TestAddress, AccountHeaderEntry.VERSION)] = 0
    witness_keys[vkt_key_header(TestAddress, AccountHeaderEntry.BALANCE)] = sender_balance
    witness_keys[vkt_key_header(TestAddress, AccountHeaderEntry.NONCE)] = 0
    witness_keys[vkt_key_header(TestAddress, AccountHeaderEntry.CODE_HASH)] = bytes([0] * 32)
    witness_keys[vkt_key_header(TestAddress, AccountHeaderEntry.CODE_SIZE)] = 0
    witness_keys[vkt_key_header(target, AccountHeaderEntry.VERSION)] = 0
    witness_keys[vkt_key_header(target, AccountHeaderEntry.BALANCE)] = value
    witness_keys[vkt_key_header(target, AccountHeaderEntry.NONCE)] = 0
    witness_keys[vkt_key_header(target, AccountHeaderEntry.CODE_HASH)] = bytes([0] * 32)
    witness_keys[vkt_key_header(target, AccountHeaderEntry.CODE_SIZE)] = 0

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
