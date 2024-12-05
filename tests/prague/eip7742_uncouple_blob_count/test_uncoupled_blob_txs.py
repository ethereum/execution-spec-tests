"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
"""  # noqa: E501

import itertools
from typing import List, Tuple

import pytest

from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    StateTestFiller,
    Transaction,
)

from .spec import Spec, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version


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


def invalid_cancun_blob_combinations() -> List[Tuple[int, ...]]:
    """
    Returns all possible invalid Cancun blob tx combinations for a given block that use up to
    `CANCUN_MAX_BLOBS_PER_BLOCK+1` blobs. These combinations are valid from Prague.
    """
    all = [
        seq
        for i in range(
            Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 1, 0, -1
        )  # We can have from 1 to at most MAX_BLOBS_PER_BLOCK blobs per block
        for seq in itertools.combinations_with_replacement(
            range(1, Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 2), i
        )  # We iterate through all possible combinations
        if sum(seq) == Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 1
    ]
    # We also add the reversed version of each combination, only if it's not
    # already in the list. E.g. (4, 1) is added from (1, 4) but not
    # (1, 1, 1, 1, 1) because its reversed version is identical.
    all += [tuple(reversed(x)) for x in all if tuple(reversed(x)) not in all]
    return all


@pytest.mark.parametrize(
    "blobs_per_tx",
    invalid_cancun_blob_combinations(),
)
@pytest.mark.valid_from("Prague")
def test_invalid_cancun_block_blob_count(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    block: Block,
):
    """
    Tests all invalid blob combinations for the Cancun fork in a single block,
    where the sum of all blobs in a block is `CANCUN_MAX_BLOBS_PER_BLOCK + 1`.

    This is a copy of the invalid test from:
        `tests/cancun/eip4844_blobs/test_blob_txs.py:test_invalid_block_blob_count`.

    In Cancun, these blocks are invalid but in Prague they are valid.
    """
    blockchain_test(
        pre=pre,
        post={},
        blocks=[block],
        genesis_environment=env,
        header_verify=block.header_verify,
    )
