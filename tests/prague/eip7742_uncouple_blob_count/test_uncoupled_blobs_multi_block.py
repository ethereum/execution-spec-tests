"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
"""  # noqa: E501

from typing import List, Optional

import pytest

from ethereum_test_base_types import HexNumber
from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Hash,
    Transaction,
    add_kzg_version,
)

from .spec import Spec, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version


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

    The blob gas price is calculated based on the excess blob gas from the parent block, and
    set as the `max_fee_per_blob_gas` for each transaction.
    """
    if tx_counts_per_block is None:
        tx_counts_per_block = [1] * len(blob_counts_per_block)

    if len(blob_counts_per_block) != len(tx_counts_per_block):
        raise ValueError(
            "The lengths of `blob_counts_per_block` and `tx_counts_per_block` must match."
        )

    blocks = []
    nonce = 0
    parent_excess_blob_gas = 10 * Spec.GAS_PER_BLOB

    for block_index, (total_blob_count, tx_count) in enumerate(
        zip(blob_counts_per_block, tx_counts_per_block)
    ):
        txs_in_block = []
        base_blobs_per_tx = total_blob_count // tx_count
        remaining_blobs = total_blob_count % tx_count
        blob_gas_used = total_blob_count * Spec.GAS_PER_BLOB
        excess_blob_gas = max(
            0,
            parent_excess_blob_gas + blob_gas_used - Spec.CANCUN_TARGET_BLOB_GAS_PER_BLOCK,
        )
        blob_gasprice = Spec.get_blob_gasprice(excess_blob_gas=excess_blob_gas)
        for tx_index in range(tx_count):
            tx = txs[0].copy()
            tx.nonce = HexNumber(nonce)
            nonce += 1
            tx_blob_count = base_blobs_per_tx + (1 if tx_index < remaining_blobs else 0)
            blob_hashes = add_kzg_version(
                [Hash(block_index * 10000 + tx_index * 100 + i) for i in range(tx_blob_count)],
                Spec.BLOB_COMMITMENT_VERSION_KZG,
            )
            tx.blob_versioned_hashes = [Hash(b_hash) for b_hash in blob_hashes]
            tx.max_fee_per_blob_gas = HexNumber(blob_gasprice)
            txs_in_block.append(tx)

        block = Block(txs=txs_in_block)
        blocks.append(block)
        parent_excess_blob_gas = excess_blob_gas

    return blocks


@pytest.fixture
def account_balance_modifier() -> int:
    """
    Override the default account balance modifier in conftest.py.
    """
    return 10**64


@pytest.mark.parametrize(
    "total_blob_counts, tx_counts_per_block",
    [
        # 10 blobs over 2 txs, 20 blobs over 4 txs
        (
            [10, 20],
            [2, 4],
        ),
        # 30 blobs over 3 txs, 60 blobs over 6 txs, 90 blobs over 9 txs
        (
            [30, 60, 90],
            [3, 6, 9],
        ),
        # 50 blobs over 5 txs, 100 blobs over 10 txs, 150 blobs over 15 txs, 200 blobs over 20 txs
        (
            [50, 100, 150, 200],
            [5, 10, 15, 20],
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
    "blob_counts_per_block, tx_counts_per_block",
    [
        # Incremental: 1 to 64 blobs, 1 tx per block, 64 blocks
        (
            [max(1, i) for i in range(64)],
            [1] * 64,
        ),
        # Decremental: 64 to 1 blobs, 1 tx per block, 65 blocks
        (
            [max(1, i) for i in reversed(range(64))],
            [1] * 64,
        ),
        # Incremental then decremental: 1 to 32 to 1 blobs, 1 tx per block, 66 blocks
        (
            [max(1, i) for i in range(33)] + [max(1, i) for i in reversed(range(33))],
            [1] * 66,
        ),
        # Decremental then incremental: 32 to 1 to 32 blobs, 1 tx per block, 66 blocks
        (
            [max(1, i) for i in reversed(range(33))] + [max(1, i) for i in range(33)],
            [1] * 66,
        ),
    ],
    ids=[
        "incremental_1_tx",
        "decremental_1_tx",
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
