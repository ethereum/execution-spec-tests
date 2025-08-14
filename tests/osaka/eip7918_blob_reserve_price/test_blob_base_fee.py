"""
abstract:  [EIP-7918: Blob base fee bounded by execution cost](https://eips.ethereum.org/EIPS/eip-7918)
    Test the blob base fee reserve price mechanism for [EIP-7918: Blob base fee bounded by execution cost](https://eips.ethereum.org/EIPS/eip-7918).

"""  # noqa: E501

from typing import Dict, List

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
    Header,
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
    """Contract that stores the blob base fee for verification."""
    code = Op.SSTORE(0, Op.BLOBBASEFEE)
    return pre.deploy_contract(code)


@pytest.fixture
def tx_gas() -> int:
    """Gas limit for transactions sent during test."""
    return 100_000


@pytest.fixture
def tx_value() -> int:
    """Value for transactions sent during test."""
    return 1


@pytest.fixture
def blob_hashes_per_tx(blobs_per_tx: int) -> List[Hash]:
    """Blob hashes for the transaction."""
    return add_kzg_version(
        [Hash(x) for x in range(blobs_per_tx)],
        Spec.BLOB_COMMITMENT_VERSION_KZG,
    )


@pytest.fixture
def tx(
    sender: Address,
    destination_account: Address,
    tx_gas: int,
    tx_value: int,
    blob_hashes_per_tx: List[Hash],
    block_base_fee_per_gas: int,
    tx_max_fee_per_blob_gas: int,
) -> Transaction:
    """Blob transaction for the block."""
    return Transaction(
        ty=Spec.BLOB_TX_TYPE,
        sender=sender,
        to=destination_account,
        value=tx_value,
        gas_limit=tx_gas,
        max_fee_per_gas=block_base_fee_per_gas,
        max_priority_fee_per_gas=0,
        max_fee_per_blob_gas=tx_max_fee_per_blob_gas,
        access_list=[],
        blob_versioned_hashes=blob_hashes_per_tx,
    )


@pytest.fixture
def block(
    tx: Transaction,
    fork: Fork,
    parent_excess_blobs: int,
    block_base_fee_per_gas: int,
    blob_gas_per_blob: int,
) -> Block:
    """Single block fixture."""
    blob_count = len(tx.blob_versioned_hashes) if tx.blob_versioned_hashes else 0
    excess_blob_gas_calculator = fork.excess_blob_gas_calculator()
    expected_excess_blob_gas = excess_blob_gas_calculator(
        parent_excess_blobs=parent_excess_blobs,
        parent_blob_count=0,
        parent_base_fee_per_gas=block_base_fee_per_gas,
    )
    return Block(
        txs=[tx],
        header_verify=Header(
            excess_blob_gas=expected_excess_blob_gas,
            blob_gas_used=blob_count * blob_gas_per_blob,
        ),
    )


@pytest.fixture
def post(
    destination_account: Address,
    blob_gas_price: int,
    tx_value: int,
) -> Dict[Address, Account]:
    """Post state storing the effective blob base fee."""
    return {
        destination_account: Account(
            storage={0: blob_gas_price},
            balance=tx_value,
        )
    }


@pytest.mark.parametrize(
    "block_base_fee_per_gas",
    [1, 7, 15, 16, 17, 100, 1000, 10000],
)
@pytest.mark.parametrize_by_fork(
    "parent_excess_blobs",
    lambda fork: range(0, fork.target_blobs_per_block() + 1),
)
def test_reserve_price_various_base_fee_scenarios(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Alloc,
    block: Block,
    post: Dict[Address, Account],
):
    """Test reserve price mechanism across various block base fee and excess blob gas scenarios."""
    blockchain_test(
        pre=pre,
        post=post,
        blocks=[block],
        genesis_environment=env,
    )


@pytest.mark.parametrize_by_fork(
    "parent_excess_blobs",
    # Keep max assuming this will be greater than 20 in the future, to test a blob fee of > 1 :)
    lambda fork: [0, 3, fork.target_blobs_per_block(), fork.max_blobs_per_block()],
)
@pytest.mark.parametrize("block_base_fee_per_gas_delta", [-2, -1, 0, 1, 10, 100])
def test_reserve_price_boundary(
    blockchain_test: BlockchainTestFiller,
    env: Environment,
    pre: Alloc,
    block: Block,
    post: Dict[Address, Account],
):
    """
    Tests the reserve price boundary mechanism. Note the default block base fee per gas is 7 (delta is 0).
    With a non zero delta the block base fee per gas is set to (boundary * blob base fee) + delta.

    Example scenarios from parametrization, assume parent_excess_blobs = 3:
        delta=-2: blob_base_fee=1, boundary=8, block_base_fee_per_gas=8+(-2)=6, 6 < 8, reserve inactive, effective_fee=1
        delta=0: blob_base_fee=1, boundary=8, block_base_fee_per_gas=7, 7 < 8, reserve inactive, effective_fee=1
        delta=100: blob_base_fee=1, boundary=8, block_base_fee_per_gas=8+100=108, 108 > 8, reserve active, effective_fee=max(108/8, 1)=13

    All values give a blob base_ fee of 1 because we need a much higher excess blob gas
    to increase the blob fee. This only increases to 2 at 20 excess blobs.
    """  # noqa: E501
    blockchain_test(
        genesis_environment=env,
        pre=pre,
        blocks=[block],
        post=post,
    )


# ---------------------------------------------------------------------------------------


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


# uv run fill -vv -s --clean ./tests/osaka/eip7918_blob_reserve_price/test_blob_base_fee.py::test_blob_base_fee_update_with_bpo  # noqa: E501

# NotImplementedError: Target blobs per block is not supported in Frontier
# Why does it not respect: pytest.mark.valid_at_transition_to("BPO1") ?
