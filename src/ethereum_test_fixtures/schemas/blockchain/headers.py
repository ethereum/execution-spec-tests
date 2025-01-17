"""Define genesisHeader schema for filled .json tests."""

from dataclasses import dataclass, fields
from typing import Optional, Type

from ethereum_rlp import decode as rlp_decode
from ethereum_rlp import decode_to as rlp_decode_to
from ethereum_rlp import encode as rlp_encode
from ethereum_types.bytes import Bytes
from ethereum_types.numeric import Uint
from pydantic import BaseModel, Field, model_validator

from ..common.types import (
    DataBytes,
    FixedHash8,
    FixedHash20,
    FixedHash32,
    FixedHash256,
    PrefixedEvenHex,
)


class InvalidBlockRecord(BaseModel):
    """Invalid block rlp only provided."""

    rlp: str
    expectException: str  # noqa: N815
    rlp_decoded: Optional[dict] = None

    class Config:
        """Forbids any extra fields that are not declared in the model."""

        extra = "forbid"


class BlockRecord(BaseModel):
    """Block record in blockchain tests."""

    blockHeader: dict  # noqa: N815
    rlp: str
    transactions: list  # noqa: N815
    uncleHeaders: list  # noqa: N815

    blocknumber: Optional[str] = Field(
        None, description="Block number for the users to read in the tests"
    )

    class Config:
        """Forbids any extra fields that are not declared in the model."""

        extra = "forbid"


class BlockRecordShanghai(BlockRecord):
    """Block record in blockchain tests."""

    withdrawals: list


@dataclass
class BaseRLPHeader:
    """Abstract base RLP header."""


class FrontierHeader(BaseModel):
    """Frontier block header in test json."""

    bloom: FixedHash256
    coinbase: FixedHash20
    difficulty: PrefixedEvenHex
    extraData: DataBytes  # noqa: N815"
    gasLimit: PrefixedEvenHex  # noqa: N815"
    gasUsed: PrefixedEvenHex  # noqa: N815"
    hash: FixedHash32
    mixHash: FixedHash32  # noqa: N815"
    nonce: FixedHash8
    number: PrefixedEvenHex
    parentHash: FixedHash32  # noqa: N815"
    receiptTrie: FixedHash32  # noqa: N815"
    stateRoot: FixedHash32  # noqa: N815"
    timestamp: PrefixedEvenHex
    transactionsTrie: FixedHash32  # noqa: N815"
    uncleHash: FixedHash32  # noqa: N815"

    class Config:
        """Forbids any extra fields that are not declared in the model."""

        extra = "forbid"

    @dataclass
    class FrontierRLPHeader(BaseRLPHeader):
        """Frontier block header representation in RLP format."""

        parentHash: Bytes  # noqa: N815"
        uncleHash: Bytes  # noqa: N815"
        coinbase: Bytes
        stateRoot: Bytes  # noqa: N815"
        transactionsTrie: Bytes  # noqa: N815"
        receiptTrie: Bytes  # noqa: N815"
        bloom: Bytes
        difficulty: Uint
        number: Uint
        gasLimit: Uint  # noqa: N815"
        gasUsed: Uint  # noqa: N815"
        timestamp: Uint
        extraData: Bytes  # noqa: N815"
        mixHash: Bytes  # noqa: N815"
        nonce: Bytes

    def get_rlp_header_scheme(self) -> Type[BaseRLPHeader]:
        """Return structure of fields as they are encoded in RLP."""
        return self.FrontierRLPHeader


class HomesteadHeader(FrontierHeader):
    """Homestead block header in test json."""


class ByzantiumHeader(HomesteadHeader):
    """Byzantium block header in test json."""


class ConstantinopleHeader(ByzantiumHeader):
    """Constantinople block header in test json."""


class IstanbulHeader(ConstantinopleHeader):
    """Istanbul block header in test json."""


class BerlinHeader(IstanbulHeader):
    """Berlin block header in test json."""


class LondonHeader(BerlinHeader):
    """London block header in test json."""

    baseFeePerGas: PrefixedEvenHex  # noqa: N815

    @dataclass
    class LondonRLPHeader(FrontierHeader.FrontierRLPHeader):
        """London block header representation in RLP format."""

        baseFeePerGas: Uint  # noqa: N815

    def get_rlp_header_scheme(self) -> Type[BaseRLPHeader]:
        """Return structure of fields as they are encoded in RLP."""
        return self.LondonRLPHeader


class ParisHeader(LondonHeader):
    """Paris block header in test json."""

    @model_validator(mode="after")
    def check_block_header(self):
        """Validate Paris block header rules."""
        if self.difficulty != "0x00":
            raise ValueError("Starting from Paris, block difficulty must be 0x00")


class ShanghaiHeader(ParisHeader):
    """Shanghai block header in test json."""

    withdrawalsRoot: FixedHash32  # noqa: N815

    @dataclass
    class ShanghaiRLPHeader(LondonHeader.LondonRLPHeader):
        """Shanghai block header representation in RLP format."""

        withdrawalsRoot: Bytes  # noqa: N815

    def get_rlp_header_scheme(self) -> Type[BaseRLPHeader]:
        """Return structure of fields as they are encoded in RLP."""
        return self.ShanghaiRLPHeader


class CancunHeader(ShanghaiHeader):
    """Cancun block header in test json."""

    blobGasUsed: PrefixedEvenHex  # noqa: N815
    excessBlobGas: PrefixedEvenHex  # noqa: N815
    parentBeaconBlockRoot: FixedHash32  # noqa: N815

    @dataclass
    class CancunRLPHeader(ShanghaiHeader.ShanghaiRLPHeader):
        """Cancun block header representation in RLP format."""

        blobGasUsed: Uint  # noqa: N815
        excessBlobGas: Uint  # noqa: N815
        parentBeaconBlockRoot: Bytes  # noqa: N815

    def get_rlp_header_scheme(self) -> Type[BaseRLPHeader]:
        """Return structure of fields as they are encoded in RLP."""
        return self.CancunRLPHeader


def verify_block_header_vs_rlp_string(header_json: FrontierHeader, rlp_string: str):
    """Check that rlp encoding of block header match header object."""
    rlp_block = rlp_decode(bytes.fromhex(rlp_string[2:]))
    if isinstance(rlp_block[0], (list, tuple)):
        rlp_header = rlp_decode_to(header_json.get_rlp_header_scheme(), rlp_encode(rlp_block[0]))
    else:
        raise ValueError("Rlp block encoding must be a list, first element must be a list!")

    for field in fields(header_json.get_rlp_header_scheme()):
        field_name = field.name

        rlp_value = getattr(rlp_header, field_name)
        field_rlp_value = (
            rlp_value.hex() if isinstance(rlp_value, bytes) else rlp_value.to_be_bytes().hex()
        )

        """special rlp rule"""
        # Field number in header encoded as empty byte '80' so it is decoded as '' but it is '00'
        if field_rlp_value == "" and field_name not in ["data", "to", "extraData"]:
            field_rlp_value = "00"
        """"""

        field_json_value = getattr(header_json, field_name).root[2:]
        if field_json_value != field_rlp_value:
            raise ValueError(
                f"Field `{field_name}` in json not equal to it's rlp encoding:"
                f"\n {field_json_value} != {field_rlp_value}"
            )
