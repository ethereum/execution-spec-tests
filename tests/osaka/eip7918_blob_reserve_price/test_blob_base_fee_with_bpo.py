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
        to=sender,
        gas_limit=100_000,
        max_fee_per_gas=1500,
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
        max_fee_per_gas=1500,
        nonce=nonce,
    )


@pytest.mark.valid_at_transition_to("BPO1")
@pytest.mark.parametrize("block_base_fee_per_gas", [7, 1000])
def test_blob_base_fee_update_with_bpo(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    sender: Address,
    destination_account: Address,
    fork: Fork,
):
    """
    Test BPO1 transition with blob base fee parameter changes.

    This test shows how the same excess blob count produces different
    blob base fees when using different parameter sets:
    - Osaka: `baseFeeUpdateFraction = 5007716`
    - BPO1:  `baseFeeUpdateFraction = 8832827`

    We create setup blocks to give us 48 excess blobs, demonstrating blob base fee changes from
    3 to 2 to 1 during the BPO transition process:
    - Block 14_999 (Osaka): 48 excess gives a blob base fee of 3
        - Calculation: fake_exponential(1, 48 * 131072, 5007716) = 3
    - Block 15_000 (BPO1):  48 excess gives a blob base fee of 2 (shows parameter change effect)
        - Calculation: fake_exponential(1, 48 * 131072, 8832827) = 2
    - Block 15_001 (BPO1):  39 excess gives a blob base fee of 1 (shows excess reduction effect)
        - Calculation: fake_exponential(1, 39 * 131072, 8832827) = 1

    Note: Blob base fee is calculated from the excess at the beginning of the block not the end.

    The aim of the test is to check that clients correctly select the appropriate blob base fee
    update fraction when transitioning through a BPO fork. Clients should use the blob base fee
    update fraction from the current block's context. In this example the BPO1 transition block
    will use the blob base fee update fraction from BPO1 and not the previous Osaka block.

    When the `base_fee_per_gas=7` the EIP-7918 reserve mechanism is off triggering the EIP-4844
    code path. When the `base_fee_per_gas=5000` the EIP-7918 reserve mechanism is on for all test
    blocks, where clients will use the reserve price excess blob gas calculation instead of the
    standard EIP-4844 excess blob gas calculation.
    """
    # Build up 48 excess blobs under Osaka parameters
    # Osaka: target=6, max=9, net=3 blobs per block
    target_excess_blobs = 48

    # Calculate setup blocks needed under Osaka parameters
    net_blobs_per_block = fork.max_blobs_per_block(timestamp=0) - fork.target_blobs_per_block(
        timestamp=0
    )  # 9 - 6 = 3
    setup_blocks_needed = target_excess_blobs // net_blobs_per_block  # 48 // 3 = 16

    # Create setup blocks to give 48 excess blobs
    blocks = []
    nonce = 0
    for _ in range(setup_blocks_needed):
        # Each block uses 9 blobs in 2 txs (6+3), adds net 3 excess blobs per block
        blocks.append(
            Block(
                txs=[
                    blob_tx(sender, nonce, fork.target_blobs_per_block(timestamp=0)),  # 6 blobs
                    blob_tx(sender, nonce + 1, net_blobs_per_block),  # 3 blobs
                ],
            )
        )
        nonce += 2

    # Blocks to trigger BPO1 transition with `blob_base_fee` increment
    blocks.extend(
        [
            # Osaka, keep excess blobs the same, store blob base fee of 3
            Block(
                timestamp=14_999,
                txs=[
                    blob_tx(  # Target blobs added to block so excess remains
                        sender,
                        nonce,
                        fork.target_blobs_per_block(timestamp=14_999),
                    ),
                    storage_tx(sender, destination_account, nonce + 1),
                ],
            ),
            # BPO1 transition, excess falls from 48 to 39, store blob base fee of 2
            Block(
                timestamp=15_000,  # BPO1 activation
                txs=[storage_tx(sender, destination_account, nonce + 2)],
            ),
            # BPO1, excess falls from 39 to 30, store blob base fee of 1 (remains the same)
            # Falls by BPO1 target blobs per block = 9
            Block(
                timestamp=15_001,
                txs=[storage_tx(sender, destination_account, nonce + 3)],
            ),
        ]
    )

    post = {
        destination_account: Account(
            storage={
                14_999: 3,
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
