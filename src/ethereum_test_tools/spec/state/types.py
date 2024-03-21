"""
StateTest types
"""

import json
from pathlib import Path
from typing import Annotated, Any, Dict, List, Mapping, Optional, Sequence, TextIO

from pydantic import AfterValidator, AliasGenerator, BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel

from evm_transition_tool import FixtureFormats

from ...common.base_types import Address, Bytes, Hash, ZeroPaddedHexNumber
from ...common.types import (
    AccessList,
    Alloc,
    CamelModel,
    Environment,
    Result,
    SerializationCamelModel,
    Transaction,
)
from ...exceptions import TransactionException
from ..base.base_test import BaseFixture


class FixtureEnvironment(Environment):
    """
    Type used to describe the environment of a state test.
    """

    gas_limit: ZeroPaddedHexNumber = Field(
        100_000_000_000_000_000, serialization_alias="currentGasLimit"
    )
    number: ZeroPaddedHexNumber = Field(1, serialization_alias="currentNumber")
    timestamp: ZeroPaddedHexNumber = Field(1_000, serialization_alias="currentTimestamp")
    prev_randao: ZeroPaddedHexNumber | None = Field(None, serialization_alias="currentRandom")
    difficulty: ZeroPaddedHexNumber | None = Field(None, serialization_alias="currentDifficulty")
    base_fee_per_gas: ZeroPaddedHexNumber | None = Field(
        None, serialization_alias="currentBaseFee"
    )
    blob_gas_used: ZeroPaddedHexNumber | None = Field(
        None, serialization_alias="currentBlobGasUsed"
    )
    excess_blob_gas: ZeroPaddedHexNumber | None = Field(
        None, serialization_alias="currentExcessBlobGas"
    )

    @classmethod
    def from_env(cls, env: Environment) -> "FixtureEnvironment":
        """
        Returns a FixtureEnvironment from an Environment.
        """
        return cls(**env.model_dump(exclude_none=True))


to_list = lambda x: [x]


class FixtureTransaction(CamelModel):
    """
    Type used to describe a transaction in a state test.
    """

    ty: ZeroPaddedHexNumber | None = Field(None, alias="type")
    chain_id: ZeroPaddedHexNumber = Field(ZeroPaddedHexNumber(1))
    nonce: ZeroPaddedHexNumber
    gas_price: ZeroPaddedHexNumber | None = None
    max_priority_fee_per_gas: ZeroPaddedHexNumber | None = None
    max_fee_per_gas: ZeroPaddedHexNumber | None = None
    gas_limit: Annotated[List[ZeroPaddedHexNumber], BeforeValidator(to_list)]
    to: Address | Annotated[None, AfterValidator(lambda _: "")] = Field(
        None, validate_default=True
    )
    value: Annotated[List[ZeroPaddedHexNumber], BeforeValidator(to_list)]
    data: Annotated[List[Bytes], BeforeValidator(to_list)] = Field()
    access_list: Annotated[List[List[AccessList]], BeforeValidator(to_list)] | None = Field(None)
    max_fee_per_blob_gas: ZeroPaddedHexNumber | None = None
    blob_versioned_hashes: Sequence[Hash] | None = None
    v: ZeroPaddedHexNumber | None = None
    r: ZeroPaddedHexNumber | None = None
    s: ZeroPaddedHexNumber | None = None
    sender: Address | None = None
    secret_key: Hash | None = None

    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        populate_by_name=True,
        validate_default=True,
    )

    @classmethod
    def from_transaction(cls, tx: Transaction) -> "FixtureTransaction":
        """
        Returns a FixtureTransaction from a Transaction.
        """
        return cls(**tx.model_dump(exclude_none=True))


class FixtureForkPostIndexes(BaseModel):
    """
    Type used to describe the indexes of a single post state of a single Fork.
    """

    data: int = 0
    gas: int = 0
    value: int = 0


class FixtureForkPost(SerializationCamelModel):
    """
    Type used to describe the post state of a single Fork.
    """

    state_root: Hash
    logs_hash: Hash
    tx_bytes: Bytes = Field(..., serialization_alias="txbytes")
    expected_exception: Optional[TransactionException] = Field(
        None,
        serialization_alias="expectException",
    )  # TODO: Add ExceptionList
    indexes: FixtureForkPostIndexes

    @classmethod
    def collect(
        cls,
        *,
        transition_tool_result: Result,
        transaction: Transaction,
    ) -> "FixtureForkPost":
        """
        Collects the post state of a single Fork from the transition tool result.
        """
        return cls(
            state_root=transition_tool_result.state_root,
            logs_hash=transition_tool_result.logs_hash,
            tx_bytes=Bytes(transaction.serialized_bytes()),
            expected_exception=transaction.error,
            indexes=FixtureForkPostIndexes(),
        )


class Fixture(BaseFixture):
    """
    Fixture for a single StateTest.
    """

    env: Annotated[FixtureEnvironment, BeforeValidator(FixtureEnvironment.from_env)]
    pre_state: Alloc
    transaction: Annotated[
        FixtureTransaction,
        BeforeValidator(FixtureTransaction.from_transaction),
    ]
    post: Mapping[str, List[FixtureForkPost]] = Field(..., default_factory=dict)

    @classmethod
    def collect_into_file(cls, fd: TextIO, fixtures: Dict[str, "BaseFixture"]):
        """
        For StateTest format, we simply join the json fixtures into a single file.

        We could do extra processing like combining tests that use the same pre-state,
        and similar transaction, but this is not done for now.
        """
        json_fixtures: Dict[str, Dict[str, Any]] = {}
        for name, fixture in fixtures.items():
            assert isinstance(fixture, Fixture), f"Invalid fixture type: {type(fixture)}"
            json_fixtures[name] = fixture.to_json()
        json.dump(json_fixtures, fd, indent=4)

    @classmethod
    def output_base_dir_name(cls) -> Path:
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        return Path("state_tests")

    @classmethod
    def format(cls) -> FixtureFormats:
        """
        Returns the fixture format which the evm tool can use to determine how to verify the
        fixture.
        """
        return FixtureFormats.STATE_TEST
