"""
StateTest types
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, TextIO

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, model_serializer
from pydantic.alias_generators import to_camel

from evm_transition_tool import FixtureFormats

from ...common.base_types import Address, Bytes, Hash, ZeroPaddedHexNumber
from ...common.types import (
    AccessList,
    Alloc,
    CamelModel,
    Environment,
    EnvironmentGeneric,
    Result,
    SerializationCamelModel,
    Transaction,
)
from ...exceptions import ExceptionList, TransactionException
from ..base.base_test import BaseFixture


class FixtureEnvironment(EnvironmentGeneric[ZeroPaddedHexNumber]):
    """
    Type used to describe the environment of a state test.
    """

    prev_randao: Hash | None = Field(None, alias="currentRandom")  # type: ignore

    @classmethod
    def from_env(cls, env: Environment) -> "FixtureEnvironment":
        """
        Returns a FixtureEnvironment from an Environment.
        """
        return cls(**env.model_dump(exclude_none=True))


def to_list(x):  # noqa: D103
    return [x]


class FixtureTransaction(CamelModel):
    """
    Type used to describe a transaction in a state test.
    """

    nonce: ZeroPaddedHexNumber
    gas_price: ZeroPaddedHexNumber | None = None
    max_priority_fee_per_gas: ZeroPaddedHexNumber | None = None
    max_fee_per_gas: ZeroPaddedHexNumber | None = None
    gas_limit: List[ZeroPaddedHexNumber]
    to: Address | None = None
    value: List[ZeroPaddedHexNumber]
    data: List[Bytes]
    access_lists: List[List[AccessList]] | None = None
    max_fee_per_blob_gas: ZeroPaddedHexNumber | None = None
    blob_versioned_hashes: Sequence[Hash] | None = None
    sender: Address | None = None
    secret_key: Hash | None = None

    model_config = ConfigDict(
        alias_generator=AliasGenerator(alias=to_camel),
        populate_by_name=True,
        validate_default=True,
    )

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
        return cls(
            **tx.model_dump(
                exclude={"gas_limit", "value", "data", "access_list"}, exclude_none=True
            ),
            gas_limit=[tx.gas_limit],
            value=[tx.value],
            data=[tx.data],
            access_lists=[tx.access_list] if tx.access_list is not None else None,
        )


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

    state_root: Hash = Field(..., alias="hash")
    logs_hash: Hash = Field(..., alias="logs")
    tx_bytes: Bytes = Field(..., alias="txbytes")
    expect_exception: TransactionException | ExceptionList | None = None
    indexes: FixtureForkPostIndexes = Field(default_factory=FixtureForkPostIndexes)

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
            tx_bytes=transaction.rlp,
            expect_exception=transaction.error,
        )


class Fixture(BaseFixture):
    """
    Fixture for a single StateTest.
    """

    env: FixtureEnvironment
    pre_state: Alloc = Field(..., alias="pre")
    transaction: FixtureTransaction
    post: Mapping[str, List[FixtureForkPost]] = Field(...)

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
