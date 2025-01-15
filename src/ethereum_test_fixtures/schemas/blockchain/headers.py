"""Define genesisHeader schema for filled .json tests."""

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator
from rlp import decode as rlp_decode

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

    def get_field_rlp_order(self) -> dict[str, Any]:
        """Order fields are encoded into rlp."""
        rlp_order: dict[str, Any] = {
            "parentHash": self.parentHash,
            "uncleHash": self.uncleHash,
            "coinbase": self.coinbase,
            "stateRoot": self.stateRoot,
            "transactionsTrie": self.transactionsTrie,
            "receiptTrie": self.receiptTrie,
            "bloom": self.bloom,
            "difficulty": self.difficulty,
            "number": self.number,
            "gasLimit": self.gasLimit,
            "gasUsed": self.gasUsed,
            "timestamp": self.timestamp,
            "extraData": self.extraData,
            "mixHash": self.mixHash,
            "nonce": self.nonce,
        }
        return rlp_order


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

    def get_field_rlp_order(self) -> dict[str, Any]:
        """Order fields are encoded into rlp."""
        rlp_order: dict[str, Any] = super().get_field_rlp_order()
        rlp_order["baseFeePerGas"] = self.baseFeePerGas
        return rlp_order


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

    def get_field_rlp_order(self) -> dict[str, Any]:
        """Order fields are encoded into rlp."""
        rlp_order: dict[str, Any] = super().get_field_rlp_order()
        rlp_order["withdrawalsRoot"] = self.withdrawalsRoot
        return rlp_order


class CancunHeader(ShanghaiHeader):
    """Cancun block header in test json."""

    blobGasUsed: PrefixedEvenHex  # noqa: N815
    excessBlobGas: PrefixedEvenHex  # noqa: N815
    parentBeaconBlockRoot: FixedHash32  # noqa: N815

    def get_field_rlp_order(self) -> dict[str, Any]:
        """Order fields are encoded into rlp."""
        rlp_order: dict[str, Any] = super().get_field_rlp_order()
        rlp_order["blobGasUsed"] = self.blobGasUsed
        rlp_order["excessBlobGas"] = self.excessBlobGas
        rlp_order["parentBeaconBlockRoot"] = self.parentBeaconBlockRoot
        return rlp_order


def verify_block_header_vs_rlp_string(header: FrontierHeader, rlp_string: str):
    """Check that rlp encoding of block header match header object."""
    rlp = rlp_decode(bytes.fromhex(rlp_string[2:]))[0]
    for rlp_index, (field_name, field) in enumerate(header.get_field_rlp_order().items()):
        rlp_hex = rlp[rlp_index].hex()
        """special rlp rule"""
        if rlp_hex == "" and field_name not in ["data", "to", "extraData"]:
            rlp_hex = "00"
        """"""
        json_hex = field.root[2:]
        if rlp_hex != json_hex:
            raise ValueError(
                f"Field `{field_name}` in json not equal to it's rlp encoding:"
                f"\n {json_hex} != {rlp_hex}"
            )
