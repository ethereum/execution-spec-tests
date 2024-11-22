"""
Define genesisHeader schema for filled .json tests
"""

from pydantic import BaseModel, model_validator

from ..common.types import (
    DataBytes,
    FixedHash8,
    FixedHash20,
    FixedHash32,
    FixedHash256,
    PrefixedEvenHex,
)


class BlockRecord(BaseModel):
    """Block record in blockchain tests"""

    blockHeader: dict  # noqa: N815
    rlp: str
    transactions: list  # noqa: N815
    uncleHeaders: list  # noqa: N815


class FrontierHeader(BaseModel):
    """Frontier block header in test json"""

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
        """Forbids any extra fields that are not declared in the model"""

        extra = "forbid"


class HomesteadHeader(FrontierHeader):
    """Homestead block header in test json"""


class ByzantiumHeader(HomesteadHeader):
    """Byzantium block header in test json"""


class ConstantinopleHeader(ByzantiumHeader):
    """Constantinople block header in test json"""


class IstanbulHeader(ConstantinopleHeader):
    """Istanbul block header in test json"""


class BerlinHeader(IstanbulHeader):
    """Berlin block header in test json"""


class LondonHeader(BerlinHeader):
    """London block header in test json"""

    baseFeePerGas: PrefixedEvenHex  # noqa: N815


class ParisHeader(LondonHeader):
    """Paris block header in test json"""

    @model_validator(mode="after")
    def check_block_header(self):
        """
        Validate Paris block header rules
        """

        if self.difficulty != "0x00":
            raise ValueError("Starting from Paris, block difficulty must be 0x00")


class ShanghaiHeader(ParisHeader):
    """Shanghai block header in test json"""

    withdrawalsRoot: FixedHash32  # noqa: N815


class CancunHeader(ShanghaiHeader):
    """Cancun block header in test json"""

    blobGasUsed: PrefixedEvenHex  # noqa: N815
    excessBlobGas: PrefixedEvenHex  # noqa: N815
    parentBeaconBlockRoot: FixedHash32  # noqa: N815
