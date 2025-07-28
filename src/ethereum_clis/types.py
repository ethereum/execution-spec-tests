"""Types used in the transition tool interactions."""

from typing import Annotated, Any, Dict, List, Self

from pydantic import Field, PlainSerializer, PlainValidator

from ethereum_test_base_types import (
    BlobSchedule,
    Bloom,
    Bytes,
    CamelModel,
    EthereumTestRootModel,
    Hash,
    HexNumber,
)
from ethereum_test_exceptions import (
    BlockException,
    ExceptionMapperValidator,
    ExceptionWithMessage,
    TransactionException,
    UndefinedException,
)
from ethereum_test_types import Alloc, Environment, Transaction, TransactionReceipt
from ethereum_test_vm import Opcode, Opcodes


class TransactionExceptionWithMessage(ExceptionWithMessage[TransactionException]):
    """Transaction exception with message."""

    pass


class BlockExceptionWithMessage(ExceptionWithMessage[BlockException]):
    """Block exception with message."""

    pass


class RejectedTransaction(CamelModel):
    """Rejected transaction."""

    index: HexNumber
    error: Annotated[
        TransactionExceptionWithMessage | UndefinedException, ExceptionMapperValidator
    ]


_opcode_synonyms = {
    "KECCAK256": "SHA3",
}


def validate_opcode(obj: Any) -> Opcodes:
    """Validate an opcode from a string."""
    if isinstance(obj, Opcode) or isinstance(obj, Opcodes):
        return obj
    if isinstance(obj, str):
        if obj in _opcode_synonyms:
            obj = _opcode_synonyms[obj]
        for op in Opcodes:
            if str(op) == obj:
                return op
    raise Exception(f"Unable to validate {obj} (type={type(obj)})")


class OpcodeCount(EthereumTestRootModel):
    """Opcode count returned from the evm tool."""

    root: Dict[
        Annotated[Opcodes, PlainValidator(validate_opcode), PlainSerializer(lambda o: str(o))], int
    ]

    def __add__(self, other: Self) -> Self:
        """Add two instances of opcode count dictionaries."""
        assert isinstance(other, OpcodeCount), f"Incompatible type {type(other)}"
        new_dict = self.model_dump() | other.model_dump()
        for match_key in self.root.keys() & other.root.keys():
            new_dict[match_key] = self.root[match_key] + other.root[match_key]
        return OpcodeCount(new_dict)


class Result(CamelModel):
    """Result of a transition tool output."""

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
    requests_hash: Hash | None = None
    requests: List[Bytes] | None = None
    block_exception: Annotated[
        BlockExceptionWithMessage | UndefinedException | None, ExceptionMapperValidator
    ] = None
    opcode_count: OpcodeCount | None = None


class TransitionToolInput(CamelModel):
    """Transition tool input."""

    alloc: Alloc
    txs: List[Transaction]
    env: Environment


class TransitionToolOutput(CamelModel):
    """Transition tool output."""

    alloc: Alloc
    result: Result
    body: Bytes | None = None


class TransitionToolContext(CamelModel):
    """Transition tool context."""

    fork: str
    chain_id: int = Field(..., alias="chainid")
    reward: int
    blob_schedule: BlobSchedule | None


class TransitionToolRequest(CamelModel):
    """Transition tool server request data."""

    state: TransitionToolContext
    input: TransitionToolInput
