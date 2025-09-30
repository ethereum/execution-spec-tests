"""Tests for BLOCKHASH opcode."""

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Storage,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op


@pytest.mark.valid_from("Frontier")
def test_genesis_hash_available(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    Verify BLOCKHASH(0) returns genesis hash in block 1.

    Regression test: Blockchain test infrastructure must populate genesis hash
    before execution. Without this, BLOCKHASH(0) returns 0, breaking dynamic
    address computations like BLOCKHASH(0) | TIMESTAMP.

    Bug context: revm blockchaintest runner wasn't inserting block_hashes,
    causing failures in tests with BLOCKHASH-derived addresses.
    """
    storage = Storage()

    # Store ISZERO(BLOCKHASH(0)) - should be 0 (false) if genesis hash exists
    code = Op.SSTORE(storage.store_next(0), Op.ISZERO(Op.BLOCKHASH(0)))

    contract = pre.deploy_contract(code=code)
    sender = pre.fund_eoa()

    blocks = [
        Block(
            txs=[
                Transaction(
                    sender=sender,
                    to=contract,
                    gas_limit=100_000,
                    protected=False,
                )
            ]
        )
    ]

    post = {
        contract: Account(
            storage={
                0: 0,  # ISZERO(BLOCKHASH(0)) should be 0 (genesis hash exists and is non-zero)
            }
        )
    }

    blockchain_test(pre=pre, post=post, blocks=blocks)
