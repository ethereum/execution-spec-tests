"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
"""  # noqa: E501

from typing import List, Optional

import pytest

from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Hash,
    StateTestFiller,
    Transaction,
    add_kzg_version,
)

from .spec import Spec, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version


@pytest.mark.parametrize(
    "blobs_per_tx",
    [(0,)],
)
@pytest.mark.valid_from("Prague")
def test_zero_blobs_in_blob_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test that a blob transaction with zero blobs is accepted in Prague (EIP-7742).
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )


@pytest.mark.parametrize(
    "blobs_per_tx",
    [
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 1,),
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 2,),
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 3,),
    ],
)
@pytest.mark.valid_from("Prague")
def test_blobs_above_cancun_max(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test that transactions with blob counts above the Cancun maximum are accepted in Prague.
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )


@pytest.mark.parametrize(
    "blobs_per_tx",
    [(i,) for i in range(64, 1024, 64)],
)
@pytest.mark.valid_from("Prague")
def test_large_number_of_blobs_in_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test transactions with a large number of blobs (64 to 1024 blobs).
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )


def multiple_blocks_with_blobs(
    txs: List[Transaction],
    blob_counts_per_block: List[int],
    tx_counts_per_block: Optional[List[int]] = None,
) -> List[Block]:
    """
    Creates multiple blocks with blob transactions. If `tx_counts_per_block` is not provided,
    it defaults to 1 transaction per block, resulting in multiple blocks with a single blob
    transaction.

    Otherwise, the number of transactions in each block is specified by `tx_counts_per_block`.
    This means we will have multiple blocks with multiple blob transactions, where the number of
    blobs in each transaction is determined by the total blob count for the block.
    """
    if tx_counts_per_block is None:
        tx_counts_per_block = [1] * len(blob_counts_per_block)

    if len(blob_counts_per_block) != len(tx_counts_per_block):
        raise ValueError(
            "The lengths of `blob_counts_per_block` and `tx_counts_per_block` must match."
        )

    blocks = []
    for block_index, (total_blob_count, tx_count) in enumerate(
        zip(blob_counts_per_block, tx_counts_per_block)
    ):
        txs_in_block = []
        base_blobs_per_tx = total_blob_count // tx_count
        remaining_blobs = total_blob_count % tx_count

        for tx_index in range(tx_count):
            tx = txs[0].copy()
            # Number of blobs for this transaction
            tx_blob_count = base_blobs_per_tx + (1 if tx_index < remaining_blobs else 0)
            # Create a list of blob hashes for this transaction
            blob_hashes = add_kzg_version(
                [Hash(block_index * 10000 + tx_index * 100 + i) for i in range(tx_blob_count)],
                Spec.BLOB_COMMITMENT_VERSION_KZG,
            )
            tx.blob_versioned_hashes = [Hash(b_hash) for b_hash in blob_hashes]
            txs_in_block.append(tx)

        block = Block(txs=txs_in_block)
        blocks.append(block)

    return blocks


@pytest.mark.parametrize(
    "total_blob_counts, tx_counts_per_block, account_balance_modifier",
    [
        # 10 blobs over 2 txs, 20 blobs over 4 txs
        (
            [10, 20],
            [2, 4],
            10**18,
        ),
        # 30 blobs over 3 txs, 60 blobs over 6 txs, 90 blobs over 9 txs
        (
            [30, 60, 90],
            [3, 6, 9],
            10**18,
        ),
        # 50 blobs over 5 txs, 100 blobs over 10 txs, 150 blobs over 15 txs, 200 blobs over 20 txs
        (
            [50, 100, 150, 200],
            [5, 10, 15, 20],
            10**18,
        ),
    ],
)
@pytest.mark.valid_from("Prague")
def test_multiple_blocks_varied_blobs(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    txs: List[Transaction],
    total_blob_counts: List[int],
    tx_counts_per_block: List[int],
):
    """
    Test multiple blocks with varied transactions and blob counts per block.
    """
    blockchain_test(
        pre=pre,
        post={},
        blocks=multiple_blocks_with_blobs(txs, total_blob_counts, tx_counts_per_block),
        genesis_environment=env,
    )


@pytest.mark.parametrize(
    "blob_counts_per_block, tx_counts_per_block, account_balance_modifier",
    [
        # Incremental 1: 0 to 64 blobs, 1 tx per block, 64 blocks
        (
            [i for i in range(65)],
            [1] * 65,
            10**18,
        ),
        # Incremental 2: 0 to 256 blobs, 10 txs per block, 26 blocks
        (
            [i * 10 for i in range(26)],
            [10] * 26,
            10**18,
        ),
        # Decremental 1: 64 to 0 blobs, 1 tx per block, 64 blocks
        (
            [i for i in reversed(range(65))],
            [1] * 65,
            10**18,
        ),
        # Decremental 2: 256 to 0 blobs, 10 txs per block, 26 blocks
        (
            [i * 10 for i in reversed(range(26))],
            [10] * 26,
            10**18,
        ),
        # Incremental then decremental 1: 0 to 64 to 0 blobs, 1 tx per block, 130 blocks
        (
            [i for i in range(65)] + [i for i in reversed(range(65))],
            [1] * 130,
            10**18,
        ),
        # Decremental then incremental 1: 64 to 0 to 64 blobs, 1 tx per block, 130 blocks
        (
            [i for i in reversed(range(65))] + [i for i in range(65)],
            [1] * 130,
            10**18,
        ),
    ],
    ids=[
        "incremental_1_tx",
        "incremental_10_txs",
        "decremental_1_tx",
        "decremental_10_txs",
        "incremental_then_decremental",
        "decremental_then_incremental",
    ],
)
@pytest.mark.valid_from("Prague")
def test_multi_blocks_incremental_decremental(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    txs: List[Transaction],
    blob_counts_per_block: List[int],
    tx_counts_per_block: List[int],
):
    """
    Test multiple blocks with incremental, decremental, and ascending-then-descending
    blob counts per block.
    """
    blockchain_test(
        pre=pre,
        post={},
        blocks=multiple_blocks_with_blobs(txs, blob_counts_per_block, tx_counts_per_block),
        genesis_environment=env,
    )
