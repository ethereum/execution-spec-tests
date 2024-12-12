"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
"""  # noqa: E501

from typing import List, Optional

import pytest

from ethereum_test_base_types import HexNumber
from ethereum_test_forks import Fork
from ethereum_test_tools import (
    EOA,
    AccessList,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    BlockException,
    Bytecode,
    EngineAPIError,
    Environment,
    Hash,
    Header,
    Removable,
    Transaction,
    TransactionException,
    add_kzg_version,
)

from .spec import Spec, SpecHelpers, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version


@pytest.fixture
def destination_account_code() -> Bytecode | None:
    """Default code in the destination account for the blob transactions."""
    return None


@pytest.fixture
def destination_account_balance() -> int:
    """Default balance in the destination account for the blob transactions."""
    return 0


@pytest.fixture
def destination_account(
    pre: Alloc, destination_account_code: Bytecode | None, destination_account_balance: int
) -> Address:
    """Default destination account for the blob transactions."""
    if destination_account_code is not None:
        return pre.deploy_contract(
            code=destination_account_code,
            balance=destination_account_balance,
        )
    return pre.fund_eoa(destination_account_balance)


@pytest.fixture
def tx_value() -> int:
    """
    Default value contained by the transactions sent during test.

    Can be overloaded by a test case to provide a custom transaction value.
    """
    return 1


@pytest.fixture
def tx_gas(
    fork: Fork,
    tx_calldata: bytes,
    tx_access_list: List[AccessList],
) -> int:
    """Default gas allocated to transactions sent during test."""
    tx_intrinsic_cost_calculator = fork.transaction_intrinsic_cost_calculator()
    return tx_intrinsic_cost_calculator(calldata=tx_calldata, access_list=tx_access_list)


@pytest.fixture
def tx_calldata() -> bytes:
    """Default calldata in transactions sent during test."""
    return b""


@pytest.fixture
def block_fee_per_gas() -> int:
    """Default max fee per gas for transactions sent during test."""
    return 7


@pytest.fixture(autouse=True)
def parent_excess_blobs() -> Optional[int]:
    """
    Default excess blobs of the parent block.

    Can be overloaded by a test case to provide a custom parent excess blob
    count.
    """
    return 10  # Defaults to a blob gas price of 1.


@pytest.fixture(autouse=True)
def parent_blobs() -> Optional[int]:
    """
    Default data blobs of the parent blob.

    Can be overloaded by a test case to provide a custom parent blob count.
    """
    return 0


@pytest.fixture
def parent_excess_blob_gas(
    parent_excess_blobs: Optional[int],
) -> Optional[int]:
    """
    Calculates the excess blob gas of the parent block from the excess blobs.
    """
    if parent_excess_blobs is None:
        return None
    return parent_excess_blobs * Spec.GAS_PER_BLOB


@pytest.fixture
def blob_gasprice(
    parent_excess_blob_gas: Optional[int],
    parent_blobs: Optional[int],
) -> Optional[int]:
    """
    Blob gas price for the block of the test.
    """
    if parent_excess_blob_gas is None or parent_blobs is None:
        return None

    return Spec.get_blob_gasprice(
        excess_blob_gas=SpecHelpers.calc_excess_blob_gas_from_blob_count(
            parent_excess_blob_gas=parent_excess_blob_gas,
            parent_blob_count=parent_blobs,
        ),
    )


@pytest.fixture
def tx_max_priority_fee_per_gas() -> int:
    """
    Default max priority fee per gas for transactions sent during test.

    Can be overloaded by a test case to provide a custom max priority fee per
    gas.
    """
    return 0


@pytest.fixture
def blobs_per_tx() -> List[int]:
    """
    Returns a list of integers that each represent the number of blobs in each
    transaction in the block of the test.

    Used to automatically generate a list of correctly versioned blob hashes.

    Default is to have one transaction with one blob.

    Can be overloaded by a test case to provide a custom list of blob counts.
    """
    return [1]


@pytest.fixture
def blob_hashes_per_tx(blobs_per_tx: List[int]) -> List[List[bytes]]:
    """
    Produce the list of blob hashes that are sent during the test.

    Can be overloaded by a test case to provide a custom list of blob hashes.
    """
    return [
        add_kzg_version(
            [Hash(x) for x in range(blob_count)],
            Spec.BLOB_COMMITMENT_VERSION_KZG,
        )
        for blob_count in blobs_per_tx
    ]


@pytest.fixture
def total_account_minimum_balance(  # noqa: D103
    tx_gas: int,
    tx_value: int,
    tx_max_fee_per_gas: int,
    tx_max_fee_per_blob_gas: int,
    blob_hashes_per_tx: List[List[bytes]],
) -> int:
    """
    Calculates the minimum balance required for the account to be able to send
    the transactions in the block of the test.
    """
    minimum_cost = 0
    for tx_blob_count in [len(x) for x in blob_hashes_per_tx]:
        blob_cost = tx_max_fee_per_blob_gas * Spec.GAS_PER_BLOB * tx_blob_count
        minimum_cost += (tx_gas * tx_max_fee_per_gas) + tx_value + blob_cost
    return minimum_cost


@pytest.fixture(autouse=True)
def tx_max_fee_per_gas(
    block_fee_per_gas: int,
) -> int:
    """
    Max fee per gas value used by all transactions sent during test.

    By default the max fee per gas is the same as the block fee per gas.

    Can be overloaded by a test case to test rejection of transactions where
    the max fee per gas is insufficient.
    """
    return block_fee_per_gas


@pytest.fixture
def tx_max_fee_per_blob_gas(  # noqa: D103
    blob_gasprice: Optional[int],
) -> int:
    """
    Default max fee per blob gas for transactions sent during test.

    By default, it is set to the blob gas price of the block.

    Can be overloaded by a test case to test rejection of transactions where
    the max fee per blob gas is insufficient.
    """
    if blob_gasprice is None:
        # When fork transitioning, the default blob gas price is 1.
        return 1
    return blob_gasprice


@pytest.fixture
def tx_access_list() -> List[AccessList]:
    """
    Default access list for transactions sent during test.

    Can be overloaded by a test case to provide a custom access list.
    """
    return []


@pytest.fixture
def tx_error() -> Optional[TransactionException]:
    """
    Default expected error produced by the block transactions (no error).

    Can be overloaded on test cases where the transactions are expected
    to fail.
    """
    return None


@pytest.fixture
def sender_initial_balance(  # noqa: D103
    total_account_minimum_balance: int, account_balance_modifier: int
) -> int:
    return total_account_minimum_balance + account_balance_modifier


@pytest.fixture
def sender(pre: Alloc, sender_initial_balance: int) -> Address:  # noqa: D103
    return pre.fund_eoa(sender_initial_balance)


@pytest.fixture
def txs(  # noqa: D103
    sender: EOA,
    destination_account: Optional[Address],
    tx_gas: int,
    tx_value: int,
    tx_calldata: bytes,
    tx_max_fee_per_gas: int,
    tx_max_fee_per_blob_gas: int,
    tx_max_priority_fee_per_gas: int,
    tx_access_list: List[AccessList],
    blob_hashes_per_tx: List[List[bytes]],
    tx_error: Optional[TransactionException],
) -> List[Transaction]:
    """
    Prepare the list of transactions that are sent during the test.
    """
    return [
        Transaction(
            ty=Spec.BLOB_TX_TYPE,
            sender=sender,
            to=destination_account,
            value=tx_value,
            gas_limit=tx_gas,
            data=tx_calldata,
            max_fee_per_gas=tx_max_fee_per_gas,
            max_priority_fee_per_gas=tx_max_priority_fee_per_gas,
            max_fee_per_blob_gas=tx_max_fee_per_blob_gas,
            access_list=tx_access_list,
            blob_versioned_hashes=blob_hashes,
            error=tx_error if tx_i == (len(blob_hashes_per_tx) - 1) else None,
        )
        for tx_i, blob_hashes in enumerate(blob_hashes_per_tx)
    ]


@pytest.fixture
def env(
    parent_excess_blob_gas: Optional[int],
    parent_blobs: int,
) -> Environment:
    """
    Prepare the environment of the genesis block for all blockchain tests.
    """
    excess_blob_gas = parent_excess_blob_gas if parent_excess_blob_gas else 0
    if parent_blobs:
        # We increase the excess blob gas of the genesis because
        # we cannot include blobs in the genesis, so the
        # test blobs are actually in block 1.
        excess_blob_gas += Spec.CANCUN_TARGET_BLOB_GAS_PER_BLOCK
    return Environment(
        excess_blob_gas=excess_blob_gas,
        blob_gas_used=0,
    )


@pytest.fixture
def state_env(
    parent_excess_blob_gas: Optional[int],
    parent_blobs: int,
) -> Environment:
    """
    Prepare the environment for all state test cases.

    Main difference is that the excess blob gas is not increased by the target, as
    there is no genesis block -> block 1 transition, and therefore the excess blob gas
    is not decreased by the target.
    """
    return Environment(
        excess_blob_gas=SpecHelpers.calc_excess_blob_gas_from_blob_count(
            parent_excess_blob_gas=parent_excess_blob_gas if parent_excess_blob_gas else 0,
            parent_blob_count=parent_blobs,
        ),
    )


@pytest.fixture
def block_error(
    tx_error: Optional[TransactionException],
) -> Optional[TransactionException | BlockException]:
    """
    Default expected error produced by the block transactions (no error).

    Can be overloaded on test cases where the transactions are expected
    to fail.
    """
    return tx_error


@pytest.fixture
def block_number() -> int:
    """
    Default number of the first block.
    """
    return 1


@pytest.fixture
def block_timestamp() -> int:
    """
    Default timestamp of the first block.
    """
    return 1


@pytest.fixture
def expected_blob_gas_used(
    fork: Fork,
    txs: List[Transaction],
    block_number: int,
    block_timestamp: int,
) -> Optional[int | Removable]:
    """
    Calculates the blob gas used by the test block.
    """
    if not fork.header_blob_gas_used_required(
        block_number=block_number, timestamp=block_timestamp
    ):
        return Header.EMPTY_FIELD
    return sum([Spec.get_total_blob_gas(tx) for tx in txs])


@pytest.fixture
def expected_excess_blob_gas(
    fork: Fork,
    parent_excess_blob_gas: Optional[int],
    parent_blobs: Optional[int],
    block_number: int,
    block_timestamp: int,
) -> Optional[int | Removable]:
    """
    Calculates the blob gas used by the test block.
    """
    if not fork.header_excess_blob_gas_required(
        block_number=block_number, timestamp=block_timestamp
    ):
        return Header.EMPTY_FIELD
    return SpecHelpers.calc_excess_blob_gas_from_blob_count(
        parent_excess_blob_gas=parent_excess_blob_gas if parent_excess_blob_gas else 0,
        parent_blob_count=parent_blobs if parent_blobs else 0,
    )


@pytest.fixture
def header_verify(
    txs: List[Transaction],
    expected_blob_gas_used: Optional[int | Removable],
    expected_excess_blob_gas: Optional[int | Removable],
) -> Header:
    """
    Header fields to verify from the transition tool.
    """
    header_verify = Header(
        blob_gas_used=expected_blob_gas_used,
        excess_blob_gas=expected_excess_blob_gas,
        gas_used=0 if len([tx for tx in txs if not tx.error]) == 0 else None,
    )
    return header_verify


@pytest.fixture
def block(
    txs: List[Transaction],
    block_error: Optional[TransactionException | BlockException] = None,
    engine_api_error_code: Optional[EngineAPIError] = None,
    header_verify: Optional[Header] = None,
) -> Block:
    """
    Test block for all blockchain test cases.
    """
    return Block(
        txs=txs,
        exception=block_error,
        engine_api_error_code=engine_api_error_code,
        header_verify=header_verify,
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
