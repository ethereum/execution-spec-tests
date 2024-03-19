"""
Pydantic Model for blockchain test fixtures.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Union

import rich
from eth_pydantic_types import Address, HashBytes8, HashBytes32
from eth_pydantic_types.hash import _make_hash_cls
from ethereum.base_types import U64, U256, Bytes, Uint

# from ethereum.crypto.hash import Hash32
from pydantic import (  # noqa: SC200
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationError,
    ValidationInfo,
    field_serializer,
    field_validator,
)
from pydantic.alias_generators import to_camel

from ethereum_test_forks import Cancun, Fork, Frontier, Paris, Shanghai

# from typing_extensions import Annotated


# HashBytes256 = _make_hash_cls(256, Bytes256)
HashBytes256 = _make_hash_cls(256, bytes)


class CamelModel(BaseModel):  # noqa: D101
    model_config = ConfigDict(alias_generator=to_camel)


class Info(CamelModel):  # noqa: D101
    transition_tool: str = Field(alias="filling-transition-tool")
    reference_spec: str = Field(alias="reference-spec")
    reference_spec_version: str = Field(alias="reference-spec-version")


class BlockHeader(CamelModel):  # noqa: D101
    model_config = ConfigDict(arbitrary_types_allowed=True)
    parent_hash: HashBytes32
    ommers_hash: HashBytes32 = Field(alias="uncleHash")
    coinbase: Address
    state_root: HashBytes32
    transactions_root: HashBytes32 = Field(alias="transactionsTrie")
    receipt_root: HashBytes32 = Field(alias="receiptTrie")
    bloom: HashBytes256
    difficulty: Uint
    number: Uint
    gas_limit: Uint
    gas_used: Uint
    timestamp: U256
    extra_data: Bytes
    # prev_randao: HashBytes32
    hash: HashBytes32
    nonce: HashBytes8
    base_fee_per_gas: Uint

    @field_validator(
        "difficulty", "number", "gas_limit", "gas_used", "base_fee_per_gas", mode="before"
    )
    @classmethod
    def validate_uint(cls, v: int, info: ValidationInfo) -> Uint:  # noqa: D102
        if isinstance(v, str):
            return Uint(int(v, 16))
        elif isinstance(v, int):
            return Uint(v)
        raise ValueError(f"Invalid value for {info.field_name}: {v}")

    @field_validator(
        "timestamp",
        mode="before",
    )
    @classmethod
    def validate_u256(cls, v: int, info: ValidationInfo) -> U256:  # noqa: D102
        if isinstance(v, str):
            return U256(int(v, 16))
        elif isinstance(v, int):
            return U256(v)
        raise ValueError(f"Invalid value for {info.field_name}: {v}")


class ParisHeader(BlockHeader):  # noqa: D101
    """
    Header portion of a block on the chain.
    """

    # model_config = ConfigDict(arbitrary_types_allowed=True)
    pass


class ShanghaiHeader(ParisHeader):  # noqa: D101
    withdrawals_root: HashBytes32


class CancunHeader(ShanghaiHeader):  # noqa: D101
    model_config = ConfigDict(arbitrary_types_allowed=True)
    base_fee_per_gas: Uint
    blob_gas_used: U64  # noqa: SC200
    excess_blob_gas: U64  # noqa: SC200


class BlockchainFixture(CamelModel):  # noqa: D101
    model_config = ConfigDict(arbitrary_types_allowed=True)
    info: Info = Field(alias="_info")
    network: Fork
    genesis_rlp: bytes = Field(alias="genesisRLP")
    genesis_block_header: Union[ParisHeader, ShanghaiHeader, CancunHeader]
    last_block_hash: HashBytes32 = Field(alias="lastblockhash")
    seal_engine: str = "NoProof"

    @field_validator("network", mode="before")
    @classmethod
    def check_fork(cls, v: str, info: ValidationInfo) -> Fork:  # noqa: D102
        if isinstance(v, str):
            if v == "Shanghai":
                return Shanghai
            elif v == "Paris":
                return Paris
            elif v == "Cancun":
                return Cancun
        raise ValueError(f"Invalid value for {info.field_name}: {v}")

    @field_serializer("network")
    def serialize_network(self, network: Fork, _info) -> str:  # noqa: D102
        return network.name()

    @field_validator("genesis_block_header", mode="before")
    @classmethod
    def validate_genesis_block_header(
        cls, v: dict, info: ValidationInfo
    ) -> BlockHeader:  # noqa: D102
        if "network" in info.data:
            fork = info.data["network"]
        if fork is None:
            raise ValueError("Fork must be set before genesis_block_header.")

        if fork == Paris:
            return ParisHeader(**v)
        elif fork == Shanghai:
            return ShanghaiHeader(**v)
        elif fork == Cancun:
            return CancunHeader(**v)
        raise ValueError(f"Invalid fork value while validating {info.field_name}: {fork}")


class BlockchainFixtures(RootModel):  # noqa: D101
    """
    Top-level model for blockchain test fixtures.

    The top-level keys in our JSON are dynamic and represent the test name. By
    defining a RootModel, we can use the `root` attribute to access the fixtures,
    but the `root` attribute is not included in the model dump.

    We could instead define:
    ```
    BlockchainFixtures = RootModel[Dict[str, BlockchainFixture]]
    ```
    """

    pass
    # root: Dict[str, BlockchainFixture]


BlockchainFixtures = RootModel[Dict[str, BlockchainFixture]]


def main() -> None:
    """
    Main function.
    """
    parser = argparse.ArgumentParser(
        description="Load a blockchain test fixture ino a Pydantic model."
    )

    parser.add_argument(
        "--mode",
        default="blocktest",
        type=str,
        help="The type of filler we are trying to parse: blockchain/state.",
    )
    parser.add_argument("fixture_json", type=Path, help="The path to a single JSON/YML file.")

    args = parser.parse_args()

    try:
        with open(args.fixture_json, "r") as file:
            data = json.load(file)

        blockchain_fixtures = BlockchainFixtures(data)

        # print(blockchain_fixtures.model_dump_json(by_alias=True, indent=2))
        rich.print(blockchain_fixtures)

        test_name = list(blockchain_fixtures.root.keys())[0]
        blockchain_fixtures.root[test_name].network = Paris

        rich.print(blockchain_fixtures)
        # print(blockchain_fixtures.model_dump_json(by_alias=True, indent=2))

    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")

    except ValidationError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    main()
