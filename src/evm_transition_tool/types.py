"""
Types used in the transition tool interactions.
"""

from typing import List

from pydantic import Field

from ethereum_test_base_types import Address, Bloom, Bytes, CamelModel, Hash, HexNumber
from ethereum_test_types import (
    Alloc,
    ConsolidationRequest,
    DepositRequest,
    Environment,
    Transaction,
    WithdrawalRequest,
)
from ethereum_test_types.verkle import StateDiff, VerkleProof, VerkleTree, Witness


class TransactionLog(CamelModel):
    """
    Transaction log
    """

    address: Address
    topics: List[Hash]
    data: Bytes
    block_number: HexNumber
    transaction_hash: Hash
    transaction_index: HexNumber
    block_hash: Hash
    log_index: HexNumber
    removed: bool


class SetCodeDelegation(CamelModel):
    """
    Set code delegation
    """

    from_address: Address = Field(..., alias="from")
    nonce: HexNumber
    target: Address


class TransactionReceipt(CamelModel):
    """
    Transaction receipt
    """

    transaction_hash: Hash
    gas_used: HexNumber
    root: Bytes | None = None
    status: HexNumber | None = None
    cumulative_gas_used: HexNumber | None = None
    logs_bloom: Bloom | None = None
    logs: List[TransactionLog] | None = None
    contract_address: Address | None = None
    effective_gas_price: HexNumber | None = None
    block_hash: Hash | None = None
    transaction_index: HexNumber | None = None
    blob_gas_used: HexNumber | None = None
    blob_gas_price: HexNumber | None = None
    delegations: List[SetCodeDelegation] | None = None


class RejectedTransaction(CamelModel):
    """
    Rejected transaction
    """

    index: HexNumber
    error: str


class Result(CamelModel):
    """
    Result of a t8n
    """

    state_root: Hash
    ommers_hash: Hash | None = Field(None, validation_alias="sha3Uncles")
    transactions_trie: Hash = Field(..., alias="txRoot")
    receipts_root: Hash
    logs_hash: Hash
    logs_bloom: Bloom
    receipts: List[TransactionReceipt]
    rejected_transactions: List[RejectedTransaction] = Field(
        default_factory=list, alias="rejected"
    )
    difficulty: HexNumber | None = Field(None, alias="currentDifficulty")
    gas_used: HexNumber
    base_fee_per_gas: HexNumber | None = Field(None, alias="currentBaseFee")
    withdrawals_root: Hash | None = None
    excess_blob_gas: HexNumber | None = Field(None, alias="currentExcessBlobGas")
    blob_gas_used: HexNumber | None = None
    requests_root: Hash | None = None
    deposit_requests: List[DepositRequest] | None = None
    withdrawal_requests: List[WithdrawalRequest] | None = None
    consolidation_requests: List[ConsolidationRequest] | None = None

    # Verkle fields within the result
    verkle_conversion_address: Address | None = Field(None, alias="currentConversionAddress")
    verkle_conversion_slot_hash: Hash | None = Field(None, alias="currentConversionSlotHash")
    verkle_conversion_started: bool | None = Field(None, alias="currentConversionStarted")
    verkle_conversion_ended: bool | None = Field(None, alias="currentConversionEnded")
    verkle_conversion_storage_processed: bool | None = Field(
        None,
        alias="currentConversionStorageProcessed",
    )

    verkle_proof: VerkleProof | None = None
    state_diff: StateDiff | None = None


class TransitionToolInput(CamelModel):
    """
    Transition tool input
    """

    alloc: Alloc
    txs: List[Transaction]
    env: Environment
    vkt: VerkleTree | None = None


class TransitionToolOutput(CamelModel):
    """
    Transition tool output
    """

    alloc: Alloc
    result: Result
    body: Bytes | None = None
    vkt: VerkleTree | None = None
    witness: Witness | None = None
