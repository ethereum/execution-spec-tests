"""
Schema for filled Blockchain Test
"""

from pydantic import BaseModel, Field, model_validator

from .genesis import (
    BerlinHeader,
    BlockRecord,
    ByzantiumHeader,
    CancunHeader,
    ConstantinopleHeader,
    FrontierHeader,
    HomesteadHeader,
    IstanbulHeader,
    LondonHeader,
    ParisHeader,
    ShanghaiHeader,
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
    blocks: list[BlockRecord]
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
        allowed_networks = {
            "Frontier": FrontierHeader,
            "Homestead": HomesteadHeader,
            "EIP150": HomesteadHeader,
            "EIP158": HomesteadHeader,
            "Byzantium": ByzantiumHeader,
            "Constantinople": ConstantinopleHeader,
            "ConstantinopleFix": ConstantinopleHeader,
            "Istanbul": IstanbulHeader,
            "Berlin": BerlinHeader,
            "London": LondonHeader,
            "Paris": ParisHeader,
            "Shanghai": ShanghaiHeader,
            "Cancun": CancunHeader,
        }

        header_class = allowed_networks.get(self.network)
        if not header_class:
            raise ValueError("Incorrect value in network field: " + self.network)
        header_class(**self.genesisBlockHeader)
        for block in self.blocks:
            header_class(**block.blockHeader)
