"""
abstract:  [EIP-7918: Blob base fee bounded by execution cost](https://eips.ethereum.org/EIPS/eip-7918)
    Test the blob base fee reserve price mechanism for [EIP-7918: Blob base fee bounded by execution cost](https://eips.ethereum.org/EIPS/eip-7918).

"""  # noqa: E501

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Environment,
    Hash,
    Transaction,
    add_kzg_version,
)
from ethereum_test_tools import Opcodes as Op

from .spec import Spec, ref_spec_7918

REFERENCE_SPEC_GIT_PATH = ref_spec_7918.git_path
REFERENCE_SPEC_VERSION = ref_spec_7918.version


@pytest.fixture
def sender(pre: Alloc) -> Address:
    """Sender account with enough balance for tests."""
    return pre.fund_eoa(10**18)


@pytest.fixture
def destination_account(pre: Alloc) -> Address:
    """Contract that stores blob base fee by timestamp."""
    code = Op.SSTORE(Op.TIMESTAMP, Op.BLOBBASEFEE)
    return pre.deploy_contract(code)


def blob_tx(
    sender: Address,
    destination_account: Address,
    nonce: int,
    num_blobs: int,
) -> Transaction:
    """Transaction with specified number of blobs."""
    blob_hashes = add_kzg_version(
        [Hash(x) for x in range(num_blobs)],
        Spec.BLOB_COMMITMENT_VERSION_KZG,
    )
    return Transaction(
        ty=Spec.BLOB_TX_TYPE,
        sender=sender,
        to=destination_account,
        gas_limit=100_000,
        max_fee_per_gas=50,
        max_priority_fee_per_gas=0,
        max_fee_per_blob_gas=100,
        blob_versioned_hashes=blob_hashes,
        nonce=nonce,
    )


def storage_tx(
    sender: Address,
    destination_account: Address,
    nonce: int,
) -> Transaction:
    """Transaction to store `BLOBBASEFEE` at current timestamp."""
    return Transaction(
        sender=sender,
        to=destination_account,
        gas_limit=100_000,
        max_fee_per_gas=50,
        nonce=nonce,
    )


@pytest.mark.valid_at_transition_to("BPO1")
def test_blob_base_fee_increment_with_bpo(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    sender: Address,
    destination_account: Address,
    fork: Fork,
):
    """Test BPO transition consensus issue by building up `blob_base_fee = 2`."""
    # Build up excess blobs for `blob_base_fee` to get ready to transition from 1 to 2.
    target_excess_blobs = 15  # Start with 15 excess blobs.

    # Osaka fork has a target of 6, max per block of 9, max per tx of 6.
    # Net excess per block = max - target = 9 - 6 = 3 blobs.
    net_blobs_per_block = fork.max_blobs_per_block() - fork.target_blobs_per_block()
    setup_blocks_needed = target_excess_blobs // net_blobs_per_block

    # Create blocks to build up excess blobs (each block uses 9 blobs: [6, 3])
    blocks = []
    nonce = 0
    for _ in range(setup_blocks_needed):
        blocks.append(
            Block(
                txs=[
                    blob_tx(sender, destination_account, nonce, 6),  # 6 blobs
                    blob_tx(sender, destination_account, nonce + 1, 3),  # 3 blobs
                ],
            )
        )
        nonce += 2  # 2 txs per setup block

    # Blocks to trigger BPO1 transition with `blob_base_fee` increment
    blocks.extend(
        [
            # Osaka, 3 more excess blobs to push from 15 to 18, store blob base fee at 1.
            Block(
                timestamp=14_999,
                txs=[
                    blob_tx(sender, destination_account, nonce, 6),
                    blob_tx(sender, destination_account, nonce, 3),
                    storage_tx(sender, destination_account, nonce + 1),
                ],
            ),
            # BPO1 transition, excess falls from 18 to 15, store blob base fee at 2.
            Block(
                timestamp=15_000,  # BPO1 activation
                txs=[storage_tx(sender, destination_account, nonce + 2)],
            ),
            # BPO1, store blob base fee at 1.
            Block(
                timestamp=15_001,
                txs=[storage_tx(sender, destination_account, nonce + 3)],
            ),
        ]
    )

    post = {
        destination_account: Account(
            storage={
                14_999: 1,
                15_000: 2,
                15_001: 1,
            },
        )
    }

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        blocks=blocks,
        post=post,
    )
