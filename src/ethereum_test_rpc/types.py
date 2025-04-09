"""Types used in the RPC module for `eth` and `engine` namespaces' requests."""

from enum import Enum
from typing import Any, List, Optional

from pydantic import AliasChoices, Field, model_validator

from ethereum_test_base_types import Address, Bytes, CamelModel, Hash, HexNumber
from ethereum_test_fixtures.blockchain import FixtureExecutionPayload
from ethereum_test_types import Transaction, Withdrawal


class JSONRPCError(Exception):
    """Model to parse a JSON RPC error response."""

    code: int
    message: str

    def __init__(self, code: int | str, message: str, **kwargs):
        """Initialize the JSONRPCError."""
        self.code = int(code)
        self.message = message

    def __str__(self) -> str:
        """Return string representation of the JSONRPCError."""
        return f"JSONRPCError(code={self.code}, message={self.message})"


class TransactionByHashResponse(Transaction):
    """Represents the response of a transaction by hash request."""

    block_hash: Hash | None = None
    block_number: HexNumber | None = None

    gas_limit: HexNumber = Field(HexNumber(21_000), alias="gas")
    transaction_hash: Hash = Field(..., alias="hash")
    from_address: Address = Field(..., alias="from")
    to_address: Address | None = Field(..., alias="to")

    v: HexNumber = Field(0, validation_alias=AliasChoices("v", "yParity"))  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def adapt_clients_response(cls, data: Any) -> Any:
        """
        Perform modifications necessary to adapt the response returned by clients
        so it can be parsed by our model.
        """
        if isinstance(data, dict):
            if "gasPrice" in data and "maxFeePerGas" in data:
                # Keep only one of the gas price fields.
                del data["gasPrice"]
        return data

    def model_post_init(self, __context):
        """
        Check that the transaction hash returned by the client matches the one calculated by
        us.
        """
        Transaction.model_post_init(self, __context)
        assert self.transaction_hash == self.hash


class ForkchoiceState(CamelModel):
    """Represents the forkchoice state of the beacon chain."""

    head_block_hash: Hash = Field(Hash(0))
    safe_block_hash: Hash = Field(Hash(0))
    finalized_block_hash: Hash = Field(Hash(0))


class PayloadStatusEnum(str, Enum):
    """Represents the status of a payload after execution."""

    VALID = "VALID"
    INVALID = "INVALID"
    SYNCING = "SYNCING"
    ACCEPTED = "ACCEPTED"
    INVALID_BLOCK_HASH = "INVALID_BLOCK_HASH"


class PayloadStatus(CamelModel):
    """Represents the status of a payload after execution."""

    status: PayloadStatusEnum
    latest_valid_hash: Hash | None
    # TODO: Temporarily optional to allow nimbus-el to run `consume-engine`
    validation_error: Optional[str] = None


class ForkchoiceUpdateResponse(CamelModel):
    """Represents the response of a forkchoice update."""

    payload_status: PayloadStatus
    # TODO: Temporarily optional to allow nimbus-el to run `consume-engine`
    payload_id: Optional[Bytes] = None

    # TODO: Temporarily override default pydantic validation for `validation_error` via this class
    # Enforces that `validation_error` is required when status is INVALID or INVALID_BLOCK_HASH
    # Allows us to run `consume-engine` for nimbus-el.
    @model_validator(mode="before")
    @classmethod
    def ensure_validation_error(cls, data):
        """
        Ensure that the `payload_status` contains `validation_error` only if
        status is INVALID or INVALID_BLOCK_HASH.
        """
        if (
            isinstance(data, dict)
            and "payload_status" in data
            and isinstance(data["payload_status"], dict)
        ):
            payload_status = data["payload_status"]
            if "status" in payload_status and payload_status["status"] in [
                PayloadStatusEnum.INVALID,
                PayloadStatusEnum.INVALID_BLOCK_HASH,
            ]:
                if "validation_error" not in payload_status:
                    raise ValueError("validation_error is required when status is INVALID")
        return data


class PayloadAttributes(CamelModel):
    """Represents the attributes of a payload."""

    timestamp: HexNumber
    prev_randao: Hash
    suggested_fee_recipient: Address
    withdrawals: List[Withdrawal] | None = None
    parent_beacon_block_root: Hash | None = None


class BlobsBundle(CamelModel):
    """Represents the bundle of blobs."""

    commitments: List[Bytes]
    proofs: List[Bytes]
    blobs: List[Bytes]

    def blob_versioned_hashes(self) -> List[Hash]:
        """Return versioned hashes of the blobs."""
        return [Hash(b"\1" + commitment[1:]) for commitment in self.commitments]


class GetPayloadResponse(CamelModel):
    """Represents the response of a get payload request."""

    execution_payload: FixtureExecutionPayload
    blobs_bundle: BlobsBundle | None = None
    execution_requests: List[Bytes] | None = None
