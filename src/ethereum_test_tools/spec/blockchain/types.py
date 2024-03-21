"""
BlockchainTest types
"""

import json
from functools import cached_property
from pathlib import Path
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    TextIO,
    Tuple,
    get_args,
    get_type_hints,
)

from ethereum import rlp as eth_rlp
from ethereum.base_types import Uint
from ethereum.crypto.hash import keccak256
from pydantic import (
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    computed_field,
    model_serializer,
)

from ethereum_test_forks import Fork
from evm_transition_tool import FixtureFormats

from ...common.base_types import (
    Address,
    Bloom,
    Bytes,
    Hash,
    HeaderNonce,
    HexNumber,
    Number,
    ZeroPaddedHexNumber,
)
from ...common.constants import EmptyOmmersRoot, EngineAPIError
from ...common.conversions import BytesConvertible
from ...common.types import (
    Alloc,
    Environment,
    Removable,
    SerializationCamelModel,
    Transaction,
    Withdrawal,
    blob_versioned_hashes_from_transactions,
    transaction_list_to_serializable_list,
)
from ...exceptions import BlockException, TransactionException
from ..base.base_test import BaseFixture


class Header(SerializationCamelModel):
    """
    Header type used to describe block header properties in test specs.
    """

    parent_hash: Hash | None = None
    ommers_hash: Hash | None = None
    fee_recipient: Address | None = None
    state_root: Hash | None = None
    transactions_trie: Hash | None = None
    receipts_root: Hash | None = None
    logs_bloom: Bloom | None = None
    difficulty: HexNumber | None = None
    number: HexNumber | None = None
    gas_limit: HexNumber | None = None
    gas_used: HexNumber | None = None
    timestamp: HexNumber | None = None
    extra_data: Bytes | None = None
    prev_randao: Hash | None = None
    nonce: HeaderNonce | None = None
    base_fee_per_gas: Removable | HexNumber | None = None
    withdrawals_root: Removable | Hash | None = None
    blob_gas_used: Removable | HexNumber | None = None
    excess_blob_gas: Removable | HexNumber | None = None
    parent_beacon_block_root: Removable | Hash | None = None

    REMOVE_FIELD: ClassVar[Removable] = Removable()
    """
    Sentinel object used to specify that a header field should be removed.
    """
    EMPTY_FIELD: ClassVar[Removable] = Removable()
    """
    Sentinel object used to specify that a header field must be empty during verification.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            Removable: lambda x: None,
        },
    )


class HeaderForkRequirement(str):
    """
    Fork requirement class that specifies the name of the method that should be called
    to check if the field is required.
    """

    def __new__(cls, value: str) -> "HeaderForkRequirement":
        """
        Create a new instance of the class
        """
        return super().__new__(cls, value)

    def required(self, fork: Fork, block_number: int, timestamp: int) -> bool:
        """
        Check if the field is required for the given fork.
        """
        return getattr(fork, f"header_{self}_required")(block_number, timestamp)

    @classmethod
    def get_from_annotation(cls, field_hints: Any) -> "HeaderForkRequirement | None":
        """
        Find the annotation in the field args
        """
        if isinstance(field_hints, cls):
            return field_hints
        for hint in get_args(field_hints):
            if res := cls.get_from_annotation(hint):
                return res
        return None


class FixtureHeader(SerializationCamelModel):
    """
    Representation of an Ethereum header within a test Fixture.

    We combine the `Environment` and `Result` contents to create this model.
    """

    parent_hash: Hash
    ommers_hash: Hash = Field(Hash(EmptyOmmersRoot), serialization_alias="uncleHash")
    fee_recipient: Address = Field(..., serialization_alias="coinbase")
    state_root: Hash
    transactions_trie: Hash
    receipts_root: Hash = Field(..., serialization_alias="receiptTrie")
    logs_bloom: Bloom = Field(..., serialization_alias="bloom")
    difficulty: ZeroPaddedHexNumber = ZeroPaddedHexNumber(0)
    number: ZeroPaddedHexNumber
    gas_limit: ZeroPaddedHexNumber
    gas_used: ZeroPaddedHexNumber
    timestamp: ZeroPaddedHexNumber
    extra_data: Bytes
    prev_randao: Hash = Field(Hash(0), serialization_alias="mixHash")
    nonce: HeaderNonce = Field(HeaderNonce(0), validate_default=True)
    base_fee_per_gas: Annotated[ZeroPaddedHexNumber, HeaderForkRequirement("base_fee")] | None = (
        Field(None)
    )
    withdrawals_root: Annotated[Hash, HeaderForkRequirement("withdrawals")] | None = Field(None)
    blob_gas_used: (
        Annotated[ZeroPaddedHexNumber, HeaderForkRequirement("blob_gas_used")] | None
    ) = Field(None)
    excess_blob_gas: (
        Annotated[ZeroPaddedHexNumber, HeaderForkRequirement("excess_blob_gas")] | None
    ) = Field(None)
    parent_beacon_block_root: Annotated[Hash, HeaderForkRequirement("beacon_root")] | None = Field(
        None
    )

    fork: Fork | None = Field(None, exclude=True)

    def model_post_init(self, __context):
        """
        Model post init method used to check for required fields of a given fork.
        """
        super().model_post_init(__context)

        if self.fork is None:
            return

        # Get the timestamp and block number
        block_number = self.number
        timestamp = self.timestamp

        # For each field, check if any of the annotations are of type HeaderForkRequirement and
        # if so, check if the field is required for the given fork.
        annotated_hints = get_type_hints(self, include_extras=True)

        for field in self.model_fields:
            if field == "fork":
                continue

            header_fork_requirement = HeaderForkRequirement.get_from_annotation(
                annotated_hints[field]
            )
            if header_fork_requirement is not None:
                if (
                    header_fork_requirement.required(self.fork, block_number, timestamp)
                    and getattr(self, field) is None
                ):
                    raise ValueError(f"Field {field} is required for fork {self.fork}")

    @cached_property
    def rlp_encode_list(self) -> List:
        """
        Compute the RLP of the header
        """
        header_list = []
        for field in self.model_fields:
            if field == "fork":
                continue
            value = getattr(self, field)
            if value is not None:
                header_list.append(value if isinstance(value, bytes) else Uint(value))
        return header_list

    @cached_property
    def rlp(self) -> Bytes:
        """
        Compute the RLP of the header
        """
        return Bytes(eth_rlp.encode(self.rlp_encode_list))

    @computed_field(alias="hash")  # type: ignore[misc]
    @cached_property
    def block_hash(self) -> Hash:
        """
        Compute the RLP of the header
        """
        return Hash(keccak256(self.rlp))

    def join(self, modifier: Header) -> "FixtureHeader":
        """
        Produces a fixture header copy with the set values from the modifier.
        """
        updated_values: Dict[str, Any] = {}
        for field_name in modifier.model_fields:
            assert field_name in self.model_fields, f"Field {field_name} is not a header field"
            value = getattr(modifier, field_name)
            if value is not None:
                updated_values[field_name] = None if value is Header.REMOVE_FIELD else value

        return self.model_copy_validate(update=updated_values)

    def verify(self, baseline: Header):
        """
        Verifies that the header fields from the baseline are as expected.
        """
        for field_name in baseline.model_fields:
            baseline_value = getattr(baseline, field_name)
            if baseline_value is not None:
                assert baseline_value is not Header.REMOVE_FIELD, "invalid baseline header"
                value = getattr(self, field_name)
                if baseline_value is Header.EMPTY_FIELD:
                    assert (
                        value is None
                    ), f"invalid header field {field_name}, got {value}, want None"
                    continue
                assert value == baseline_value, (
                    f"invalid header field ({field_name}) value, "
                    + f"got {value}, want {baseline_value}"
                )

    def build(
        self,
        *,
        txs: List[Transaction],
        ommers: List[Header],
        withdrawals: List[Withdrawal] | None,
    ) -> Tuple[Bytes, Hash]:
        """
        Returns the serialized version of the block and its hash.
        """
        header = self.rlp_encode_list

        block = [
            header,
            transaction_list_to_serializable_list(txs),
            ommers,  # TODO: This is incorrect, and we probably need to serialize the ommers
        ]

        if withdrawals is not None:
            block.append([w.to_serializable_list() for w in withdrawals])

        serialized_bytes = Bytes(eth_rlp.encode(block))

        return serialized_bytes, self.block_hash


class Block(Header):
    """
    Block type used to describe block properties in test specs
    """

    rlp: Bytes | None = None
    """
    If set, blockchain test will skip generating the block and will pass this value directly to
    the Fixture.

    Only meant to be used to simulate blocks with bad formats, and therefore
    requires the block to produce an exception.
    """
    header_verify: Optional[Header] = None
    """
    If set, the block header will be verified against the specified values.
    """
    rlp_modifier: Optional[Header] = None
    """
    An RLP modifying header which values would be used to override the ones
    returned by the  `evm_transition_tool`.
    """
    exception: Optional[BlockException | TransactionException] = None  # TODO: Add ExceptionList
    """
    If set, the block is expected to be rejected by the client.
    """
    engine_api_error_code: Optional[EngineAPIError] = None
    """
    If set, the block is expected to produce an error response from the Engine API.
    """
    txs: Optional[List[Transaction]] = None
    """
    List of transactions included in the block.
    """
    ommers: Optional[List[Header]] = None
    """
    List of ommer headers included in the block.
    """
    withdrawals: Optional[List[Withdrawal]] = None
    """
    List of withdrawals to perform for this block.
    """

    def set_environment(self, env: Environment) -> Environment:
        """
        Creates a copy of the environment with the characteristics of this
        specific block.
        """
        new_env_values: Dict[str, Any] = {}

        """
        Values that need to be set in the environment and are `None` for
        this block need to be set to their defaults.
        """
        new_env_values["difficulty"] = self.difficulty
        new_env_values["fee_recipient"] = (
            self.fee_recipient if self.fee_recipient is not None else Environment().fee_recipient
        )
        new_env_values["gas_limit"] = (
            self.gas_limit or env.parent_gas_limit or Environment().gas_limit
        )
        if not isinstance(self.base_fee_per_gas, Removable):
            new_env_values["base_fee_per_gas"] = self.base_fee_per_gas
        new_env_values["withdrawals"] = self.withdrawals
        if not isinstance(self.excess_blob_gas, Removable):
            new_env_values["excess_blob_gas"] = self.excess_blob_gas
        if not isinstance(self.blob_gas_used, Removable):
            new_env_values["blob_gas_used"] = self.blob_gas_used
        if not isinstance(self.parent_beacon_block_root, Removable):
            new_env_values["parent_beacon_block_root"] = self.parent_beacon_block_root
        """
        These values are required, but they depend on the previous environment,
        so they can be calculated here.
        """
        if self.number is not None:
            new_env_values["number"] = self.number
        else:
            # calculate the next block number for the environment
            if len(env.block_hashes) == 0:
                new_env_values["number"] = 0
            else:
                new_env_values["number"] = max([Number(n) for n in env.block_hashes.keys()]) + 1

        if self.timestamp is not None:
            new_env_values["timestamp"] = self.timestamp
        else:
            assert env.parent_timestamp is not None
            new_env_values["timestamp"] = int(Number(env.parent_timestamp) + 12)

        return env.model_copy_validate(update=new_env_values)

    def copy_with_rlp(self, rlp: Bytes | BytesConvertible | None) -> "Block":
        """
        Creates a copy of the block and adds the specified RLP.
        """
        return self.model_copy_validate(update={"rlp": rlp})


class FixtureExecutionPayload(SerializationCamelModel):
    """
    Representation of an Ethereum execution payload within a test Fixture.
    """

    parent_hash: Hash
    fee_recipient: Address
    state_root: Hash

    receipts_root: Hash
    logs_bloom: Bloom

    number: HexNumber = Field(..., alias="blockNumber")
    gas_limit: HexNumber
    gas_used: HexNumber
    timestamp: HexNumber
    extra_data: Bytes
    prev_randao: Hash

    base_fee_per_gas: HexNumber | None = Field(None)
    blob_gas_used: HexNumber | None = Field(None)
    excess_blob_gas: HexNumber | None = Field(None)
    parent_beacon_block_root: Hash | None = Field(None)

    block_hash: Hash

    transactions: List[Annotated[Bytes, BeforeValidator(lambda x: x.serialized_bytes())]] = Field(
        default_factory=list
    )
    withdrawals: List[Withdrawal] | None = None

    @classmethod
    def from_fixture_header(
        cls,
        header: FixtureHeader,
        transactions: Optional[List[Transaction]] = None,
        withdrawals: Optional[List[Withdrawal]] = None,
    ) -> "FixtureExecutionPayload":
        """
        Returns a FixtureExecutionPayload from a FixtureHeader, a list
        of transactions and a list of withdrawals.
        """
        return cls(
            **header.model_dump(exclude_none=True),
            transactions=transactions,
            withdrawals=withdrawals,
        )


class FixtureEngineNewPayload(SerializationCamelModel):
    """
    Representation of the `engine_newPayloadVX` information to be
    sent using the block information.
    """

    execution_payload: FixtureExecutionPayload
    version: Number
    blob_versioned_hashes: List[Hash] | None = Field(
        None, serialization_alias="expectedBlobVersionedHashes"
    )
    parent_beacon_block_root: Hash | None = Field(
        None, serialization_alias="parentBeaconBlockRoot"
    )
    validation_error: TransactionException | BlockException | None = (
        None  # TODO: Add ExceptionList
    )
    error_code: (
        Annotated[
            EngineAPIError,
            PlainSerializer(
                lambda x: str(x.value),
                return_type=str,
            ),
        ]
        | None
    ) = None

    @classmethod
    def from_fixture_header(
        cls,
        fork: Fork,
        header: FixtureHeader,
        transactions: List[Transaction],
        withdrawals: List[Withdrawal] | None,
        **kwargs,
    ) -> "FixtureEngineNewPayload":
        """
        Creates a `FixtureEngineNewPayload` from a `FixtureHeader`.
        """
        new_payload_version = fork.engine_new_payload_version(header.number, header.timestamp)

        assert new_payload_version is not None, "Invalid header for engine_newPayload"

        new_payload = cls(
            execution_payload=FixtureExecutionPayload(
                **header.model_dump(exclude={"rlp"}, exclude_none=True),
                transactions=transactions,
                withdrawals=withdrawals,
            ),
            version=new_payload_version,
            blob_versioned_hashes=(
                blob_versioned_hashes_from_transactions(transactions)
                if fork.engine_new_payload_blob_hashes(header.number, header.timestamp)
                else None
            ),
            parent_beacon_block_root=header.parent_beacon_block_root,
            **kwargs,
        )

        return new_payload


class FixtureTransaction(Transaction):
    """
    Representation of an Ethereum transaction within a test Fixture.
    """

    ty: ZeroPaddedHexNumber | None = Field(None, alias="type")
    """
    Transaction type value.
    """
    chain_id: ZeroPaddedHexNumber = Field(ZeroPaddedHexNumber(1))
    nonce: ZeroPaddedHexNumber = Field(ZeroPaddedHexNumber(0))
    gas_price: ZeroPaddedHexNumber | None = None
    max_priority_fee_per_gas: ZeroPaddedHexNumber | None = None
    max_fee_per_gas: ZeroPaddedHexNumber | None = None
    gas_limit: ZeroPaddedHexNumber = Field(ZeroPaddedHexNumber(21000))
    to: Address | None = Field(None)
    value: ZeroPaddedHexNumber = Field(ZeroPaddedHexNumber(0))
    data: Bytes = Field(Bytes(b""))
    max_fee_per_blob_gas: ZeroPaddedHexNumber | None = None
    v: ZeroPaddedHexNumber | None = None
    r: ZeroPaddedHexNumber | None = None
    s: ZeroPaddedHexNumber | None = None

    @model_serializer(mode="wrap", when_used="json-unless-none")
    def serialize_to_as_empty_string(self, handler):
        """
        Serializes the field `to` an empty string if the value is None.
        """
        default = handler(self)
        if default is not None and "to" not in default:
            default["to"] = ""
        return default

    @classmethod
    def from_transaction(cls, tx: Transaction) -> "FixtureTransaction":
        """
        Returns a FixtureTransaction from a Transaction.
        """
        return cls(**tx.model_dump())


class FixtureWithdrawal(Withdrawal):
    """
    Structure to represent a single withdrawal of a validator's balance from
    the beacon chain in the output fixture.
    """

    index: ZeroPaddedHexNumber
    validator_index: ZeroPaddedHexNumber
    amount: ZeroPaddedHexNumber

    @classmethod
    def from_withdrawal(cls, w: Withdrawal) -> "FixtureWithdrawal":
        """
        Returns a FixtureWithdrawal from a Withdrawal.
        """
        return cls(**w.model_dump())


class FixtureBlock(SerializationCamelModel):
    """
    Representation of an Ethereum block within a test Fixture.
    """

    rlp: Bytes | None = Field(None)
    block_header: FixtureHeader = Field(...)
    block_number: Number = Field(..., serialization_alias="blocknumber")
    txs: List[
        Annotated[
            FixtureTransaction,
            BeforeValidator(FixtureTransaction.from_transaction),
        ]
    ] = Field(default_factory=list, serialization_alias="transactions")
    ommers: List[FixtureHeader] = Field(default_factory=list, serialization_alias="uncleHeaders")
    withdrawals: Optional[
        List[Annotated[Withdrawal, BeforeValidator(FixtureWithdrawal.from_withdrawal)]]
    ] = Field(None)


class InvalidFixtureBlock(SerializationCamelModel):
    """
    Representation of an invalid Ethereum block within a test Fixture.
    """

    rlp: Bytes
    expected_exception: TransactionException | BlockException = Field(  # TODO: Add ExceptionList
        ..., serialization_alias="expectException"
    )
    rlp_decoded: Optional[FixtureBlock] = Field(None, serialization_alias="rlp_decoded")


class FixtureCommon(BaseFixture):
    """
    Base Ethereum test fixture fields class.
    """

    name: str = Field("", exclude=True)
    fork: str = Field(..., serialization_alias="network")

    @classmethod
    def collect_into_file(cls, fd: TextIO, fixtures: Dict[str, "BaseFixture"]):
        """
        For BlockchainTest format, we simply join the json fixtures into a single file.
        """
        json_fixtures: Dict[str, Dict[str, Any]] = {}
        for name, fixture in fixtures.items():
            assert isinstance(fixture, FixtureCommon), f"Invalid fixture type: {type(fixture)}"
            json_fixtures[name] = fixture.to_json()
        json.dump(json_fixtures, fd, indent=4)


class Fixture(FixtureCommon):
    """
    Cross-client specific test fixture information.
    """

    genesis_rlp: Bytes = Field(..., serialization_alias="genesisRLP")
    genesis: FixtureHeader = Field(..., serialization_alias="genesisBlockHeader")
    blocks: List[FixtureBlock | InvalidFixtureBlock]
    last_block_hash: Hash = Field(..., serialization_alias="lastblockhash")
    pre_state: Alloc = Field(..., serialization_alias="pre")
    post_state: Optional[Alloc] = Field(None, serialization_alias="postState")
    seal_engine: Literal["NoProof"] = Field("NoProof")

    @classmethod
    def output_base_dir_name(cls) -> Path:
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        return Path("blockchain_tests")

    @classmethod
    def format(cls) -> FixtureFormats:
        """
        Returns the fixture format which the evm tool can use to determine how to verify the
        fixture.
        """
        return FixtureFormats.BLOCKCHAIN_TEST


class HiveFixture(FixtureCommon):
    """
    Hive specific test fixture information.
    """

    genesis: FixtureHeader = Field(..., serialization_alias="genesisBlockHeader")
    payloads: List[FixtureEngineNewPayload] = Field(
        default_factory=list,
        serialization_alias="engineNewPayloads",
    )
    fcu_version: Number = Field(Number(1), serialization_alias="engineFcuVersion")
    sync_payload: Optional[FixtureEngineNewPayload] = Field(None)
    pre_state: Alloc = Field(..., serialization_alias="pre")
    post_state: Optional[Alloc] = Field(None)

    @classmethod
    def output_base_dir_name(cls) -> Path:
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        return Path("blockchain_tests_hive")

    @classmethod
    def format(cls) -> FixtureFormats:
        """
        Returns the fixture format which the evm tool can use to determine how to verify the
        fixture.
        """
        return FixtureFormats.BLOCKCHAIN_TEST_HIVE
