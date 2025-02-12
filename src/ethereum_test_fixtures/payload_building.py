"""Fixtures for testing the payload building functions."""

from typing import Annotated, ClassVar, Dict, List, Literal, Set, Union

from pydantic import Discriminator, Field, field_serializer

from ethereum_test_base_types import Alloc, Bytes, CamelModel, Hash
from ethereum_test_exceptions import TransactionException

from .base import BaseFixture
from .blockchain import FixtureConfig, FixtureHeader, FixtureTransaction


class FixtureSendTransactionWithPost(FixtureTransaction):
    """
    Test step that sends a transaction via `eth_sendRawTransaction`.

    All transactions are assumed to be includeable in the next block unless an error is
    specified. If an error is specified, the transaction should not be included in any
    block.

    If the transaction is included in a block, the resulting post state should be
    equal to the expected post state.

    If an `invalidates` list is specified, when the transaction is included in a
    block, none of the transactions in the `invalidates` list should be included afterwards
    (same block or subsequent block).
    """

    step_type: Literal["transaction_send"] = "transaction_send"

    post: Alloc | None = None
    """
    Expected resulting post allocation of the transaction being included in a block.
    """
    rlp: Bytes
    """
    RLP-encoded transaction.
    """
    hash: Hash
    """
    Transaction hash.
    """
    error: List[TransactionException] | TransactionException | None = None
    """
    Error that should be returned by the client when sending the transaction.
    """
    invalidates: Set[Hash] = Field(default_factory=set)
    """
    List of transaction hashes that should be invalidated by this transaction.
    """

    @field_serializer("post", when_used="json")
    def post_accounts_remove_unset_fields(self, post: Alloc | Dict | None) -> Dict | None:
        """Remove unset fields from post accounts in order to avoid checking them."""
        if post is None:
            return None
        assert self.post is not None
        return self.post.model_dump(mode="json", exclude_none=True, exclude_unset=True)


class FixturePayloadBuild(CamelModel):
    """
    Test step to request the client to build a payload using `engine_forkchoiceUpdated`
    followed by `engine_getPayload`, with a custom sleep duration between the two requests.
    """

    step_type: Literal["payload_build"] = "payload_build"

    id: int
    """
    Monotonically increasing integer that identifies the payload, with zero being
    the genesis block.
    """
    parent_id: int
    """
    Identifier of the parent payload, with zero being the genesis block.
    """
    get_payload_wait_ms: int
    """
    Duration to wait between the `engine_forkchoiceUpdated` and `engine_getPayload`
    calls.
    """


class PayloadBuildingFixture(BaseFixture):
    """Cross-client payload building fixture format."""

    format_name: ClassVar[str] = "payload_building_test"
    description: ClassVar[str] = """
    Tests that verify the client's ability to build a payload with the given
    transactions.
    """

    fork: str = Field(..., alias="network")
    genesis: FixtureHeader = Field(..., alias="genesisBlockHeader")
    pre: Alloc
    config: FixtureConfig

    engine_new_payload_version: int
    """
    Version of the `engine_newPayload` method to use.
    """
    engine_forkchoice_updated_version: int
    """
    Version of the `engine_forkchoiceUpdated` method to use.
    """
    engine_get_payload_version: int
    """
    Version of the `engine_getPayload` method to use.
    """

    steps: List[
        Annotated[
            Union[FixtureSendTransactionWithPost, FixturePayloadBuild],
            Discriminator("step_type"),
        ]
    ]

    def get_fork(self) -> str | None:
        """Return fork of the fixture as a string."""
        return self.fork
