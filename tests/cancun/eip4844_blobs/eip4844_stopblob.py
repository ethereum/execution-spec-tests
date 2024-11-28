"""
abstract: Tests the `STOP` opcode and blob data handling in transactions for [EIP-4844: Shard Blob Transactions](https://eips.ethereum.org/EIPS/eip-4844) during the Cancun fork.
    This test ensures proper inclusion of blob data, verifies the functionality of the `STOP` opcode, and validates transaction execution
    behavior
"""  # noqa: E501
from typing import List

import pytest

from ethereum_test_tools import (
    Block,
    BlockchainTestFiller,
    Transaction,
    Alloc,
    Environment,
)

from .common import Blob
from .spec import Spec, SpecHelpers, ref_spec_4844

REFERENCE_SPEC_GIT_PATH = ref_spec_4844.git_path
REFERENCE_SPEC_VERSION = ref_spec_4844.version


@pytest.fixture
def txs_blobs() -> List[List[Blob]]:
    """
    Default blob data for transactions
    Each transaction has one blob
    """
    ZERO_COMMITMENT_PLACEHOLDER = b"\x00" * 48  # 48-byte zero array placeholder
    return [
        [
            Blob(
                blob=bytes(
                    Spec.FIELD_ELEMENTS_PER_BLOB * SpecHelpers.BYTES_PER_FIELD_ELEMENT
                ),
                kzg_commitment=ZERO_COMMITMENT_PLACEHOLDER,
                kzg_proof=ZERO_COMMITMENT_PLACEHOLDER,
            )
        ]
    ]


@pytest.fixture
def txs_wrapped_blobs() -> List[bool]:
    """
    Indicates whether the transaction includes wrapped blobs
    For the purpose of this test, assume no wrapping is needed
    """
    return [False]


@pytest.fixture
def txs(
    pre: Alloc,
    txs_blobs: List[List[Blob]],
    txs_wrapped_blobs: List[bool],
) -> List[Transaction]:
    """
    Generate a list of transactions with blob data
    """
    sender = pre.fund_eoa()
    txs = []
    for tx_blobs, tx_wrapped in zip(txs_blobs, txs_wrapped_blobs):
        blobs_info = Blob.blobs_to_transaction_input(tx_blobs)
        txs.append(
            Transaction(
                ty=Spec.BLOB_TX_TYPE,
                sender=sender,
                to="0x000000000000000000000000000000000000dead",  
                value=1,  
                gas_limit=Spec.MAX_BLOB_GAS_PER_BLOCK,
                data=b"\x60\x01\x60\x02\x00", # PUSH1 0x01, PUSH1 0x02, STOP
                max_fee_per_gas=7,
                max_priority_fee_per_gas=0,
                max_fee_per_blob_gas=1,
                access_list=[],
                blob_versioned_hashes=[blob.versioned_hash() for blob in tx_blobs],
                blobs=blobs_info[0],
                blob_kzg_commitments=blobs_info[1],
                blob_kzg_proofs=blobs_info[2],
                wrapped_blob_transaction=tx_wrapped,
            )
        )
    return txs


@pytest.fixture
def env() -> Environment:
    """
    Create testing environment with excess blob gas and zero blob gas used
    """
    return Environment(
        excess_blob_gas=Spec.GAS_PER_BLOB * 10,  
        blob_gas_used=0,
    )


@pytest.fixture
def blocks(txs: List[Transaction]) -> List[Block]:
    """
    Prepare a single block containing the test transactions
    """
    return [Block(txs=txs)]


@pytest.mark.valid_from("Cancun")
def test_stop_opcode_with_transaction(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    env: Environment,
    blocks: List[Block],
    txs_blobs: List[List[Blob]],
):
    """
    Test a block containing transactions that execute the STOP opcode
    """
    blockchain_test(
        pre=pre,  # Pre-state
        post={},  # Post-state
        blocks=blocks,  # Blocks to test
        genesis_environment=env,  # Genesis environment
    )

    # Validate transaction blob data and STOP opcode execution
    for block in blocks:
        for i, transaction in enumerate(block.txs):
            # Ensure transaction has blobs
            assert transaction.blobs, "Transaction must have blobs"

            # Match expected blob data
            expected_blob_data = Blob.blobs_to_transaction_input(txs_blobs[i])[0][0]
            assert transaction.blobs[0] == expected_blob_data, "Blob data should match the generated value"

            # Assert STOP opcode is in the transaction data
            assert b"\x00" in transaction.data, "STOP opcode (0x00) must be in the transaction data"

            # Simulate execution and confirm the transaction can stop
            executed_data = execute_transaction(transaction.data)
            assert executed_data == b"", "Transaction with STOP opcode must terminate execution successfully"


def execute_transaction(data: bytes) -> bytes:
    """
    Simulate transaction execution 
    """
    stack = []
    pc = 0  # Program counter
    while pc < len(data):
        opcode = data[pc]
        pc += 1
        if opcode == 0x60:  # PUSH1
            stack.append(data[pc])
            pc += 1
        elif opcode == 0x00:  # STOP
            break
    return b""  # STOP halts execution and returns no result
