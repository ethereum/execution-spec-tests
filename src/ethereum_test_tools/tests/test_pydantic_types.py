"""
Types experiment
"""

from functools import cached_property
from typing import Any, Callable, Dict, List, get_args, get_type_hints

import pytest
from ethereum import rlp as eth_rlp
from ethereum.base_types import Uint
from ethereum.crypto.hash import keccak256
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel
from pydantic.functional_serializers import PlainSerializer
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from ethereum_test_forks import Cancun, Fork, Shanghai
from ethereum_test_tools.common import EmptyOmmersRoot

# Type primitives


def to_hex_number(value: str | int) -> int:
    """
    Convert a hex number to an integer
    """
    if isinstance(value, str):
        if value.startswith("0x"):
            value = value[2:]
        value = int(value, 16)
    assert isinstance(value, int)
    return value


def from_hex_number(value: int) -> str:
    """
    Convert an integer to a hex number
    """
    assert isinstance(value, int)
    return f"0x{value:x}"


def to_bytes(value: bytes | str) -> bytes:
    """
    Convert a string to bytes
    """
    if isinstance(value, str):
        if value.startswith("0x"):
            value = value[2:]
        value = bytes.fromhex(value)
    assert isinstance(value, bytes)
    return value


def from_bytes(value: bytes) -> str:
    """
    Convert a bytes to a string
    """
    assert isinstance(value, bytes)
    return f"0x{value.hex()}"


def from_fixed_bytes(length: int) -> Callable[[bytes | str | int], bytes]:
    """
    Convert a bytes to a fixed length bytes
    """

    def _from_fixed_bytes(value: bytes | str | int) -> bytes:
        if isinstance(value, bytes):
            value = value.rjust(length, b"\x00")
        elif isinstance(value, int):
            value = value.to_bytes(length, "big")
        elif isinstance(value, str):
            if value.startswith("0x"):
                value = value[2:]
            if len(value) % 2:
                value = f"0{value}"
            value = bytes.fromhex(value).rjust(length, b"\x00")
        assert isinstance(value, bytes)
        assert len(value) == length
        return value

    return _from_fixed_bytes


def to_fixed_bytes(length: int) -> Callable[[bytes], str]:
    """
    Convert a fixed length bytes to a string
    """

    def _to_fixed_bytes(value: bytes) -> str:
        assert isinstance(value, bytes)
        assert len(value) == length
        return f"0x{value.hex()}"

    return _to_fixed_bytes


Address = Annotated[
    bytes,
    BeforeValidator(from_fixed_bytes(20)),
    PlainSerializer(to_fixed_bytes(20)),
]
Hash = Annotated[
    bytes,
    BeforeValidator(from_fixed_bytes(32)),
    PlainSerializer(to_fixed_bytes(32)),
]
Bloom = Annotated[
    bytes,
    BeforeValidator(from_fixed_bytes(256)),
    PlainSerializer(to_fixed_bytes(256)),
]
HeaderNonce = Annotated[
    bytes,
    BeforeValidator(from_fixed_bytes(8)),
    PlainSerializer(to_fixed_bytes(8)),
]


HexNumber = Annotated[
    int,
    BeforeValidator(to_hex_number),
    PlainSerializer(from_hex_number),
]
HexBytes = Annotated[
    bytes,
    BeforeValidator(to_bytes),
    PlainSerializer(from_bytes),
]

# Camel models


class CamelModel(BaseModel):
    """
    Model that uses camel case
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class SerializationCamelModel(BaseModel):
    """
    Model that uses camel case for serialization
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        populate_by_name=True,
    )


# Test models


class Withdrawal(CamelModel):
    """
    Withdrawal type
    """

    index: HexNumber
    validator_index: HexNumber
    address: Address
    amount: HexNumber


class Environment(CamelModel):
    """
    Environment to be sent to the t8n
    """

    fee_recipient: Address = Field(
        "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        serialization_alias="currentCoinbase",
        validate_default=True,
    )
    gas_limit: HexNumber = Field(100_000_000_000_000_000, serialization_alias="currentGasLimit")
    number: HexNumber = Field(1, serialization_alias="currentNumber")
    timestamp: HexNumber = Field(1_000, serialization_alias="currentTimestamp")
    prev_randao: HexNumber | None = Field(None, serialization_alias="currentRandom")
    difficulty: HexNumber | None = Field(None, serialization_alias="currentDifficulty")
    base_fee_per_gas: HexNumber | None = Field(None, serialization_alias="currentBaseFee")
    blob_gas_used: HexNumber | None = Field(None, serialization_alias="currentBlobGasUsed")
    excess_blob_gas: HexNumber | None = Field(None, serialization_alias="currentExcessBlobGas")

    parent_difficulty: HexNumber | None = Field(None)
    parent_timestamp: HexNumber | None = Field(None)
    parent_base_fee_per_gas: HexNumber | None = Field(None, serialization_alias="parentBaseFee")
    parent_gas_used: HexNumber | None = Field(None)
    parent_gas_limit: HexNumber | None = Field(None)
    parent_ommers_hash: Hash = Field(
        0, serialization_alias="parentUncleHash", validate_default=True
    )
    parent_blob_gas_used: HexNumber | None = Field(None)
    parent_excess_blob_gas: HexNumber | None = Field(None)
    parent_beacon_block_root: Hash | None = Field(None)

    block_hashes: Dict[HexNumber, Hash] = Field(default_factory=dict)
    ommers: List[Hash] = Field(default_factory=list)
    withdrawals: List[Withdrawal] | None = Field(None)
    extra_data: HexBytes = Field(b"\x00")

    def parent_hash(self) -> bytes:
        """
        Obtains the latest hash according to the highest block number in
        `block_hashes`.
        """
        if len(self.block_hashes) == 0:
            return bytes([0] * 32)

        last_index = max(self.block_hashes.keys())
        return Hash(self.block_hashes[last_index])


class TransactionReceipt(CamelModel):
    """
    Transaction receipt
    """

    root: HexBytes
    status: HexNumber
    cumulative_gas_used: HexNumber
    logs_bloom: Bloom
    logs: List[Dict[str, str]] | None = None
    transaction_hash: Hash
    contract_address: Address
    gas_used: HexNumber
    effective_gas_price: HexNumber | None = None
    block_hash: Hash
    transaction_index: HexNumber
    blob_gas_used: HexNumber | None = None
    blob_gas_price: HexNumber | None = None


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
    rejected_transactions: List[RejectedTransaction] | None = Field(None, alias="rejected")
    difficulty: HexNumber | None = Field(None, alias="currentDifficulty")
    gas_used: HexNumber
    base_fee_per_gas: HexNumber | None = Field(None, alias="currentBaseFee")
    withdrawals_root: Hash | None = None
    excess_blob_gas: HexNumber | None = Field(None, alias="currentExcessBlobGas")
    blob_gas_used: HexNumber | None = None


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
    ommers_hash: Hash = Field(EmptyOmmersRoot, serialization_alias="uncleHash")
    fee_recipient: Address = Field(..., serialization_alias="coinbase")
    state_root: Hash
    transactions_trie: Hash
    receipts_root: Hash
    logs_bloom: Bloom
    difficulty: HexNumber = 0
    number: HexNumber
    gas_limit: HexNumber
    gas_used: HexNumber
    timestamp: HexNumber
    extra_data: HexBytes
    prev_randao: Hash = Field(..., serialization_alias="mixHash")
    nonce: HeaderNonce = Field(0, validate_default=True)
    base_fee_per_gas: Annotated[HexNumber, HeaderForkRequirement("base_fee")] | None = Field(None)
    withdrawals_root: Annotated[Hash, HeaderForkRequirement("withdrawals")] | None = Field(None)
    blob_gas_used: Annotated[HexNumber, HeaderForkRequirement("blob_gas_used")] | None = Field(
        None
    )
    excess_blob_gas: Annotated[HexNumber, HeaderForkRequirement("excess_blob_gas")] | None = Field(
        None
    )
    parent_beacon_block_root: Annotated[Hash, HeaderForkRequirement("beacon_root")] | None = Field(
        None
    )

    fork: Fork = Field(..., exclude=True)

    def model_post_init(self, __context):
        """
        Model post init method used to check for required fields of a given fork.
        """
        super().model_post_init(__context)

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

    @computed_field(alias="rlp")  # type: ignore[misc]
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

    @computed_field(alias="rlp")  # type: ignore[misc]
    @cached_property
    def rlp(self) -> HexBytes:
        """
        Compute the RLP of the header
        """
        return eth_rlp.encode(self.rlp_encode_list)

    @computed_field(alias="block_hash")  # type: ignore[misc]
    @cached_property
    def block_hash(self) -> Hash:
        """
        Compute the RLP of the header
        """
        return keccak256(self.rlp)


class FixtureExecutionPayload(SerializationCamelModel):
    """
    Representation of an Ethereum execution payload within a test Fixture.
    """

    parent_hash: Hash
    fee_recipient: Address
    state_root: Hash

    receipts_root: Hash
    logs_bloom: Bloom

    number: HexNumber
    gas_limit: HexNumber
    gas_used: HexNumber
    timestamp: HexNumber
    extra_data: HexBytes
    prev_randao: Hash

    base_fee_per_gas: HexNumber | None = Field(None)
    blob_gas_used: HexNumber | None = Field(None)
    excess_blob_gas: HexNumber | None = Field(None)
    parent_beacon_block_root: Hash | None = Field(None)

    block_hash: Hash

    transactions: List[Annotated[HexBytes, BeforeValidator(lambda x: x.serialized_bytes())]]
    withdrawals: List[Withdrawal] | None = None


def test_sanity():
    """
    Sanity test
    """
    env = Environment(
        prev_randao=0,
        base_fee_per_gas=7,
        withdrawals=[],
        difficulty=0,
    )
    assert (
        env.fee_recipient
        == b"\x2a\xdc\x25\x66\x50\x18\xaa\x1f\xe0\xe6\xbc\x66\x6d\xac\x8f\xc2\x69\x7f\xf9\xba"
    )
    assert env.base_fee_per_gas == 7

    # We send the environment to the t8n
    assert env.model_dump(by_alias=True, exclude_none=True) == {
        "currentCoinbase": "0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        "currentGasLimit": "0x16345785d8a0000",
        "currentNumber": "0x1",
        "currentTimestamp": "0x3e8",
        "currentRandom": "0x0",
        "currentDifficulty": "0x0",
        "blockHashes": {},
        "ommers": [],
        "withdrawals": [],
        "currentBaseFee": "0x7",
        "parentUncleHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "extraData": "0x00",
    }

    assert "fee_recipient" in dict(env)

    result_dump = {
        "stateRoot": "0xf2e5f99c03e64ce121cb0f6e60f51d77d041010a2994dfa477a7f3a69a378ec7",
        "txRoot": "0xeb73a3f9c75d464ce0e4f1e793f7a82e85adf5037b15b898018e5de05790ebd7",
        "receiptsRoot": "0xeea4432237eee3d73482f5a674f165ebb4cabd2d612e18167c4ebfdcaad7b18a",
        "logsHash": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "logsBloom": "0x" + "00" * 256,
        "receipts": [
            {
                "root": "0x",
                "status": "0x1",
                "cumulativeGasUsed": "0x8e751",
                "logsBloom": "0x" + "00" * 256,
                "transactionHash": (
                    "0xa6657bfa5bcc143ebf2a425572c5a26c51b43563b15542b1c1039c301571ea36"
                ),
                "contractAddress": "0x6295ee1b4f6dd65047762f924ecd367c17eabf8f",
                "gasUsed": "0x8e751",
                "blockHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                "transactionIndex": "0x0",
            }
        ],
        "gasUsed": "0x8e751",
        "currentBaseFee": "0x7",
        "withdrawalsRoot": "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421",
    }
    result = Result(**result_dump)
    assert result.model_dump(by_alias=True, exclude_none=True) == result_dump

    # We combine the environment and the result to create a FixtureHeader
    fixture_header = FixtureHeader(
        **(env.model_dump(exclude_none=True) | result.model_dump(exclude_none=True)),
        parent_hash=env.parent_hash(),
        fork=Shanghai,
    )
    assert fixture_header.fee_recipient == env.fee_recipient
    assert fixture_header.state_root == result.state_root
    assert isinstance(fixture_header.fee_recipient, bytes)
    assert isinstance(fixture_header.state_root, bytes)

    # Assert that the same fixture header would fail on Cancun because of the missing fields
    with pytest.raises(ValueError):
        FixtureHeader(
            **(env.model_dump(exclude_none=True) | result.model_dump(exclude_none=True)),
            parent_hash=env.parent_hash(),
            fork=Cancun,
        )

    # We create a FixtureExecutionPayload
    transactions = []  # Obtained during block creation
    fixture_execution_payload = FixtureExecutionPayload(
        **fixture_header.model_dump(exclude={"rlp"}, exclude_none=True), transactions=transactions
    )
    assert fixture_execution_payload.fee_recipient == fixture_header.fee_recipient
    assert fixture_execution_payload.state_root == fixture_header.state_root
    assert isinstance(fixture_execution_payload.fee_recipient, bytes)
    assert isinstance(fixture_execution_payload.state_root, bytes)
