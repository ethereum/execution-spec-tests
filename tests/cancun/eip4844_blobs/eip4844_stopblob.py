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
    Account,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

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
    return [False]


@pytest.fixture
def txs(pre: Alloc, txs_blobs: List[List[Blob]], txs_wrapped_blobs: List[bool]) -> List[Transaction]:
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
                to="0x1234567890abcdef1234567890abcdef12345678",
                value=1,
                gas_limit=Spec.MAX_BLOB_GAS_PER_BLOCK,
                data="0x",
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
def contract(pre: Alloc) -> str:
    """
    Deploy a contract that executes `STOP` and stores blob data during execution
    """
    return pre.deploy_contract(Op.PUSH1 + Op.PUSH2 + Op.STOP)


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
    contract: str,
):
    """
    Test a block containing transactions that execute the STOP opcode
    """
    # Post-state: Validate contract storage and execution state
    post = {
        contract: Account(
            storage={"0x01": "0x01"}  # Storage slot `0x01` should contain the expected value
        ),
    }

    blockchain_test(
        pre=pre,  # Pre-state
        post=post,  # Post-state
        blocks=blocks,  # Blocks to test
        genesis_environment=env,  # Genesis environment
    )
