"""
Schema for filled Blockchain Test
"""

from typing import Tuple

from pydantic import BaseModel, Field, model_validator

from .headers import (
    BerlinHeader,
    BlockRecord,
    BlockRecordShanghai,
    ByzantiumHeader,
    CancunHeader,
    ConstantinopleHeader,
    FrontierHeader,
    HomesteadHeader,
    InvalidBlockRecord,
    IstanbulHeader,
    LondonHeader,
    ParisHeader,
    ShanghaiHeader,
    verify_block_header_vs_rlp_string,
)


class BlockchainTestFixtureModel(BaseModel):
    """
    Blockchain test file
    """

    info: dict = Field(alias="_info")
    network: str
    genesisBlockHeader: dict  # noqa: N815
    pre: dict
    postState: dict  # noqa: N815
    lastblockhash: str
    genesisRLP: str  # noqa: N815
    blocks: list
    sealEngine: str  # noqa: N815

    class Config:
        """Forbids any extra fields that are not declared in the model"""

        extra = "forbid"

    @model_validator(mode="after")
    def check_block_headers(self):
        """
        Validate genesis header fields based by fork
        """
        # TODO str to Fork class comparison
        allowed_networks: dict[str, Tuple[FrontierHeader, BlockRecord]] = {
            "Frontier": (FrontierHeader, BlockRecord),
            "Homestead": (HomesteadHeader, BlockRecord),
            "EIP150": (HomesteadHeader, BlockRecord),
            "EIP158": (HomesteadHeader, BlockRecord),
            "Byzantium": (ByzantiumHeader, BlockRecord),
            "Constantinople": (ConstantinopleHeader, BlockRecord),
            "ConstantinopleFix": (ConstantinopleHeader, BlockRecord),
            "Istanbul": (IstanbulHeader, BlockRecord),
            "Berlin": (BerlinHeader, BlockRecord),
            "London": (LondonHeader, BlockRecord),
            "Paris": (ParisHeader, BlockRecord),
            "Shanghai": (ShanghaiHeader, BlockRecordShanghai),
            "Cancun": (CancunHeader, BlockRecordShanghai),
            "ShanghaiToCancunAtTime15k": (ShanghaiHeader, BlockRecordShanghai),
        }

        # Check that each block in test is of format of the test declared fork
        header_class, record_type = allowed_networks.get(self.network, (None, None))
        if header_class is None:
            raise ValueError("Incorrect value in network field: " + self.network)
        header = header_class(**self.genesisBlockHeader)
        verify_block_header_vs_rlp_string(header, self.genesisRLP)
        for block in self.blocks:
            if "expectException" in block:
                record: InvalidBlockRecord = InvalidBlockRecord(**block)
                # Do not verify rlp_decoded with invalid block rlp
            else:
                if (
                    self.network == "ShanghaiToCancunAtTime15k"
                    and int(block["blockHeader"]["timestamp"], 16) >= 15000
                ):
                    header_class = CancunHeader

                record: BlockRecord = record_type(**block)
                header = header_class(**record.blockHeader)
                verify_block_header_vs_rlp_string(header, record.rlp)
