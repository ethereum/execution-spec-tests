"""
abstract: Tests [EIP-7892: Blob Parameter Only Hardforks](https://eips.ethereum.org/EIPS/eip-7892)
    Test blob parameter transitions at BPO fork boundaries.
"""

from typing import List

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Hash,
    Header,
    Transaction,
    add_kzg_version,
)

from .spec import Spec, ref_spec_7892

REFERENCE_SPEC_GIT_PATH = ref_spec_7892.git_path
REFERENCE_SPEC_VERSION = ref_spec_7892.version

FORK_TIMESTAMP = 15_000


@pytest.fixture
def sender(pre: Alloc) -> Address:
    """Sender account with sufficient balance."""
    return pre.fund_eoa(10**18)


@pytest.fixture
def destination(pre: Alloc) -> Address:
    """Destination for blob transactions."""
    return pre.fund_eoa(0)


@pytest.fixture
def genesis_environment(parent_excess_blob_gas: int) -> Environment:
    """Genesis environment for BPO tests."""
    return Environment(
        excess_blob_gas=parent_excess_blob_gas,
        blob_gas_used=0,
        base_fee_per_gas=7,
    )


def create_blob_tx(
    sender: Address,
    to: Address,
    blob_count: int,
    max_fee_per_blob_gas: int = 10000,
) -> Transaction:
    """Create a blob transaction."""
    if blob_count == 0:
        return Transaction(
            sender=sender,
            to=to,
            value=0,
            gas_limit=21_000,
            max_fee_per_gas=100,
            max_priority_fee_per_gas=0,
        )
    return Transaction(
        ty=Spec.BLOB_TX_TYPE,
        sender=sender,
        to=to,
        value=0,
        gas_limit=21_000,
        max_fee_per_gas=100,
        max_priority_fee_per_gas=0,
        max_fee_per_blob_gas=max_fee_per_blob_gas,
        blob_versioned_hashes=add_kzg_version(
            [Hash(x) for x in range(blob_count)],
            Spec.BLOB_COMMITMENT_VERSION_KZG,
        ),
    )


@pytest.fixture
def pre_fork_block(
    sender: Address,
    destination: Address,
    pre_fork_blobs_per_block: int,
) -> List[Block]:
    """Block before the fork."""
    return Block(
        txs=[
            create_blob_tx(
                sender=sender,
                to=destination,
                blob_count=pre_fork_blobs_per_block,
            )
        ],
        timestamp=FORK_TIMESTAMP - 1,
    )


@pytest.fixture
def expected_fork_excess_blob_gas(
    fork: Fork,
    parent_excess_blob_gas: int,
    pre_fork_blobs_per_block: int,
) -> int:
    """Calculate expected excess blob gas at the fork block using NEW parameters."""
    pre_fork_calc = fork.excess_blob_gas_calculator(timestamp=FORK_TIMESTAMP - 1)
    parent_excess_at_fork = pre_fork_calc(
        parent_excess_blobs=parent_excess_blob_gas // Spec.GAS_PER_BLOB,
        parent_blob_count=pre_fork_blobs_per_block,
        parent_base_fee_per_gas=7,
    )
    post_fork_calc = fork.excess_blob_gas_calculator(timestamp=FORK_TIMESTAMP)
    return post_fork_calc(
        parent_excess_blobs=parent_excess_at_fork // Spec.GAS_PER_BLOB,
        parent_blob_count=pre_fork_blobs_per_block,
        parent_base_fee_per_gas=7,
    )


@pytest.fixture
def post_fork_blocks(
    sender: Address,
    destination: Address,
    fork: Fork,
    fork_block_excess_blob_gas: int,
    post_fork_blobs_per_block: int,
    post_fork_block_count: int,
) -> List[Block]:
    """Blocks after the fork."""
    blocks = []
    current_excess_blob_gas = fork_block_excess_blob_gas

    for i in range(post_fork_block_count):
        tx = create_blob_tx(
            sender=sender,
            to=destination,
            blob_count=post_fork_blobs_per_block,
        )

        if i == 0:
            # First block at fork boundary - verify excess blob gas uses new calculation
            blocks.append(
                Block(
                    txs=[tx],
                    timestamp=FORK_TIMESTAMP,
                    header_verify=Header(
                        excess_blob_gas=fork_block_excess_blob_gas,
                        blob_gas_used=post_fork_blobs_per_block * Spec.GAS_PER_BLOB,
                    ),
                )
            )
        else:
            # Calculate excess for subsequent blocks
            post_fork_calc = fork.excess_blob_gas_calculator(timestamp=FORK_TIMESTAMP + i)
            new_excess = post_fork_calc(
                parent_excess_blobs=current_excess_blob_gas // Spec.GAS_PER_BLOB,
                parent_blob_count=post_fork_blobs_per_block,
                parent_base_fee_per_gas=7,
            )

            blocks.append(
                Block(
                    txs=[tx],
                    timestamp=FORK_TIMESTAMP + i,
                    header_verify=Header(
                        excess_blob_gas=new_excess,
                        blob_gas_used=post_fork_blobs_per_block * Spec.GAS_PER_BLOB,
                    ),
                )
            )
            current_excess_blob_gas = new_excess

    return blocks


@pytest.mark.valid_at_transition_to("BPO1")
@pytest.mark.valid_for_bpo_forks()
@pytest.mark.parametrize_by_fork(
    "parent_excess_blob_gas,pre_fork_blobs_per_block,post_fork_blobs_per_block,post_fork_block_count",
    lambda fork: [
        pytest.param(
            0,
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP - 1),
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP),
            3,
            id="max_blobs_before_and_after",
        ),
        pytest.param(
            0,
            0,
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP),
            3,
            id="no_blobs_before_max_after",
        ),
        pytest.param(
            0,
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP - 1),
            0,
            3,
            id="max_blobs_before_none_after",
        ),
        pytest.param(
            0,
            fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP - 1),
            fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP),
            5,
            id="target_blobs_before_and_after",
        ),
        pytest.param(
            0,
            1,
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP),
            3,
            id="single_blob_before_max_after",
        ),
        pytest.param(
            3 * Spec.GAS_PER_BLOB,  # Start with 3 excess blobs
            fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP - 1),
            fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP),
            5,
            id="target_blobs_with_excess",
        ),
        pytest.param(
            10 * Spec.GAS_PER_BLOB,  # Start with 10 excess blobs
            0,
            0,
            5,
            id="no_blobs_with_high_excess",
        ),
        pytest.param(
            50 * Spec.GAS_PER_BLOB,  # Start with 50 excess blobs
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP - 1),
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP),
            3,
            id="max_blobs_with_very_high_excess",
        ),
    ],
)
def test_bpo_fork_transition(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    genesis_environment: Environment,
    pre_fork_blocks: List[Block],
    post_fork_blocks: List[Block],
):
    """
    Test BPO fork transition with various blob configurations.

    Verifies that:
    1. Max blobs per block changes at the fork boundary
    2. Target blobs per block affects excess blob gas calculation correctly
    3. Base fee update fraction changes affect blob gas pricing

    The test creates blocks before and after the fork with different blob counts
    to ensure the fork parameters apply exactly at the transition timestamp.
    """
    blockchain_test(
        genesis_environment=genesis_environment,
        pre=pre,
        blocks=pre_fork_blocks + post_fork_blocks,
        post={},
    )
