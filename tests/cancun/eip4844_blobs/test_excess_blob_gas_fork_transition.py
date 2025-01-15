"""
abstract: Tests `excessBlobGas` and `blobGasUsed` block fields for [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844) at fork transition.
    Test `excessBlobGas` and `blobGasUsed` block fields for [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844) at fork
    transition.
"""  # noqa: E501

from typing import List, Mapping

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    EOA,
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    BlockException,
    EngineAPIError,
    Environment,
    Hash,
    Header,
    Transaction,
    add_kzg_version,
)
from ethereum_test_tools import Opcodes as Op

from .spec import Spec, SpecHelpers, ref_spec_4844

REFERENCE_SPEC_GIT_PATH = ref_spec_4844.git_path
REFERENCE_SPEC_VERSION = ref_spec_4844.version

# Timestamp of the fork
FORK_TIMESTAMP = 15_000


@pytest.fixture
def env() -> Environment:  # noqa: D103
    return Environment()


@pytest.fixture
def pre_fork_blobs_per_block(fork: Fork) -> int | None:
    """Amount of blobs to produce with the pre-fork rules."""
    if fork.supports_blobs(timestamp=0):
        return fork.max_blobs_per_block(timestamp=0)
    return None


@pytest.fixture
def sender(pre: Alloc) -> EOA:
    """Sender account."""
    return pre.fund_eoa()


@pytest.fixture
def pre_fork_blocks(
    pre_fork_blobs_per_block: int | None,
    destination_account: Address,
    sender: EOA,
) -> List[Block]:
    """Generate blocks to reach the fork."""
    if pre_fork_blobs_per_block is None:
        return [Block(timestamp=t) for t in range(999, FORK_TIMESTAMP, 1_000)]
    return [
        Block(
            txs=[
                Transaction(
                    ty=Spec.BLOB_TX_TYPE,
                    to=destination_account,
                    value=1,
                    gas_limit=3_000_000,
                    max_fee_per_gas=1_000_000,
                    max_priority_fee_per_gas=10,
                    max_fee_per_blob_gas=100,
                    access_list=[],
                    blob_versioned_hashes=add_kzg_version(
                        [Hash(x) for x in range(pre_fork_blobs_per_block)],
                        Spec.BLOB_COMMITMENT_VERSION_KZG,
                    ),
                    sender=sender,
                )
                if pre_fork_blobs_per_block > 0
                else Transaction(
                    ty=2,
                    to=destination_account,
                    value=1,
                    gas_limit=3_000_000,
                    max_fee_per_gas=1_000_000,
                    max_priority_fee_per_gas=10,
                    access_list=[],
                    sender=sender,
                )
            ],
            timestamp=t,
        )
        for t in range(999, FORK_TIMESTAMP, 1_000)
    ]


@pytest.fixture
def post_fork_block_count(fork: Fork) -> int:
    """Amount of blocks to produce with the post-fork rules."""
    return SpecHelpers.get_min_excess_blobs_for_blob_gas_price(fork=fork, blob_gas_price=2) // (
        fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP)
        - fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP)
    )


@pytest.fixture
def post_fork_blobs_per_block(fork: Fork) -> int:
    """Amount of blocks to produce with the post-fork rules."""
    return fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP) + 1


@pytest.fixture
def destination_account(pre: Alloc) -> Address:  # noqa: D103
    return pre.deploy_contract(Op.STOP)


@pytest.fixture
def post_fork_blocks(
    destination_account: Address,
    post_fork_block_count: int,
    post_fork_blobs_per_block: int,
    sender: EOA,
):
    """Generate blocks past the fork."""
    return [
        Block(
            txs=[
                Transaction(
                    ty=Spec.BLOB_TX_TYPE,
                    to=destination_account,
                    value=1,
                    gas_limit=3_000_000,
                    max_fee_per_gas=1_000_000,
                    max_priority_fee_per_gas=10,
                    max_fee_per_blob_gas=100,
                    blob_versioned_hashes=add_kzg_version(
                        [Hash(x) for x in range(post_fork_blobs_per_block)],
                        Spec.BLOB_COMMITMENT_VERSION_KZG,
                    ),
                    sender=sender,
                )
                if post_fork_blobs_per_block > 0
                else Transaction(
                    ty=2,
                    to=destination_account,
                    value=1,
                    gas_limit=3_000_000,
                    max_fee_per_gas=1_000_000,
                    max_priority_fee_per_gas=10,
                    sender=sender,
                )
            ],
        )
        for _ in range(post_fork_block_count)
    ]


@pytest.fixture
def post(  # noqa: D103
    pre_fork_blocks: List[Block],
    post_fork_block_count: int,
    destination_account: Address,
) -> Mapping[Address, Account]:
    return {
        destination_account: Account(balance=post_fork_block_count + len(pre_fork_blocks)),
    }


@pytest.mark.valid_at_transition_to("Cancun")
@pytest.mark.parametrize(
    "excess_blob_gas_present,blob_gas_used_present",
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_invalid_pre_fork_block_with_blob_fields(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Alloc,
    pre_fork_blocks: List[Block],
    excess_blob_gas_present: bool,
    blob_gas_used_present: bool,
):
    """
    Test block rejection when `excessBlobGas` and/or `blobGasUsed` fields are present on a pre-fork
    block.

    Blocks sent by NewPayloadV2 (Shanghai) that contain `excessBlobGas` and `blobGasUsed` fields
    must be rejected with the appropriate `EngineAPIError.InvalidParams` error error.
    """
    header_modifier = Header(
        excess_blob_gas=0 if excess_blob_gas_present else None,
        blob_gas_used=0 if blob_gas_used_present else None,
    )
    blockchain_test(
        pre=pre,
        post={},
        blocks=pre_fork_blocks[:-1]
        + [
            Block(
                timestamp=(FORK_TIMESTAMP - 1),
                rlp_modifier=header_modifier,
                exception=BlockException.INCORRECT_BLOCK_FORMAT,
                engine_api_error_code=EngineAPIError.InvalidParams,
            )
        ],
        genesis_environment=env,
    )


@pytest.mark.valid_at_transition_to("Cancun")
@pytest.mark.parametrize(
    "excess_blob_gas_missing,blob_gas_used_missing",
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_invalid_post_fork_block_without_blob_fields(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Alloc,
    pre_fork_blocks: List[Block],
    excess_blob_gas_missing: bool,
    blob_gas_used_missing: bool,
):
    """
    Test block rejection when `excessBlobGas` and/or `blobGasUsed` fields are missing on a
    post-fork block.

    Blocks sent by NewPayloadV3 (Cancun) without `excessBlobGas` and `blobGasUsed` fields must be
    rejected with the appropriate `EngineAPIError.InvalidParams` error.
    """
    header_modifier = Header()
    if excess_blob_gas_missing:
        header_modifier.excess_blob_gas = Header.REMOVE_FIELD
    if blob_gas_used_missing:
        header_modifier.blob_gas_used = Header.REMOVE_FIELD
    blockchain_test(
        pre=pre,
        post={},
        blocks=pre_fork_blocks
        + [
            Block(
                timestamp=FORK_TIMESTAMP,
                rlp_modifier=header_modifier,
                exception=BlockException.INCORRECT_BLOCK_FORMAT,
                engine_api_error_code=EngineAPIError.InvalidParams,
            )
        ],
        genesis_environment=env,
    )


@pytest.mark.valid_from("Cancun")
@pytest.mark.fork_transition_test()
@pytest.mark.parametrize_by_fork(
    "post_fork_block_count,post_fork_blobs_per_block",
    lambda fork: [
        pytest.param(
            SpecHelpers.get_min_excess_blobs_for_blob_gas_price(fork=fork, blob_gas_price=2)
            // (
                fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP)
                - fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP)
            )
            + 2,
            fork.max_blobs_per_block(timestamp=FORK_TIMESTAMP),
            id="max_blobs",
        ),
        pytest.param(10, 0, id="no_blobs"),
        pytest.param(10, fork.target_blobs_per_block(timestamp=FORK_TIMESTAMP), id="target_blobs"),
    ],
)
def test_fork_transition_excess_blob_gas(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Alloc,
    pre_fork_blocks: List[Block],
    post_fork_blocks: List[Block],
    post: Mapping[Address, Account],
):
    """
    Test `excessBlobGas` calculation in the header when the fork is activated.

    Also produce enough blocks to test the blob gas price increase when the block is full with
    `SpecHelpers.max_blobs_per_block()` blobs.
    """
    blockchain_test(
        pre=pre,
        post=post,
        blocks=pre_fork_blocks + post_fork_blocks,
        genesis_environment=env,
    )
