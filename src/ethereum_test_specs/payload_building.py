"""Ethereum payload building test specs."""

from typing import (
    Callable,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
)

import pytest
from pydantic import ConfigDict, Field

from ethereum_clis import TransitionTool
from ethereum_test_base_types import CamelModel
from ethereum_test_execution import BaseExecute, ExecuteFormat
from ethereum_test_fixtures import (
    BaseFixture,
    FixtureFormat,
    PayloadBuildingFixture,
)
from ethereum_test_fixtures.blockchain import FixtureConfig
from ethereum_test_fixtures.common import FixtureBlobSchedule
from ethereum_test_fixtures.payload_building import (
    FixturePayloadBuild,
    FixtureSendTransactionWithPost,
)
from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Environment, Transaction

from .base import BaseTest
from .blockchain import BlockchainTest
from .helpers import is_slow_test


class TransactionWithPost(Transaction):
    """
    Transaction subclass that includes the resulting post state of the transaction
    being included in a block.
    """

    post: Alloc | None = None


class Payload(CamelModel):
    """
    Test step to request the client to build a payload using `engine_forkchoiceUpdated` followed
    by `engine_getPayload`, with a custom sleep duration between the two requests.

    Contains also the verification description that should be performed.
    """

    get_payload_wait_ms: int = 1000
    parent: "Payload | None" = None

    sorted_transactions: List[Transaction] | None = None
    unsorted_transactions: List[Transaction] | None = None
    mutually_exclusive_transactions: List[Transaction] | None = None

    def to_fixture_payload_build(
        self,
        payload_id: int,
        parent_payload_id: int,
    ) -> FixturePayloadBuild:
        """Convert a Payload to a FixturePayloadBuild."""
        return FixturePayloadBuild(
            id=payload_id,
            parent_id=parent_payload_id,
            sorted_transactions=[
                tx.with_signature_and_sender().rlp for tx in self.sorted_transactions
            ]
            if self.sorted_transactions is not None
            else None,
            unsorted_transactions=[
                tx.with_signature_and_sender().rlp for tx in self.unsorted_transactions
            ]
            if self.unsorted_transactions is not None
            else None,
            mutually_exclusive_transactions=[
                tx.with_signature_and_sender().rlp for tx in self.mutually_exclusive_transactions
            ]
            if self.mutually_exclusive_transactions is not None
            else None,
            get_payload_wait_ms=self.get_payload_wait_ms,
        )


class PayloadBuildingTest(BaseTest):
    """Spec that verifies block building behavior."""

    pre: Alloc
    chain_id: int = 1
    steps: List[TransactionWithPost | Transaction | Payload]
    genesis_environment: Environment = Field(default_factory=Environment)

    supported_fixture_formats: ClassVar[List[FixtureFormat]] = [
        PayloadBuildingFixture,
    ]
    supported_execute_formats: ClassVar[List[ExecuteFormat]] = []

    def make_fixture(
        self,
        fork: Fork,
        eips: Optional[List[int]] = None,
        slow: bool = False,
    ) -> PayloadBuildingFixture:
        """Create a fixture from the payload building test definition."""
        pre, genesis = BlockchainTest.make_genesis(self.genesis_environment, self.pre, fork)
        network_info = BlockchainTest.network_info(fork, eips)

        fixture_steps: List[FixtureSendTransactionWithPost | FixturePayloadBuild] = []

        payloads: List[Payload] = []
        for step in self.steps:
            if isinstance(step, Transaction):
                post = step.post if isinstance(step, TransactionWithPost) else None
                fixture_steps.append(
                    FixtureSendTransactionWithPost.from_transaction_with_post(
                        step.with_signature_and_sender(),
                        post=post,
                    )
                )
            elif isinstance(step, Payload):
                next_id = len(payloads) + 1
                parent_id = next_id - 1
                if step.parent is not None:
                    if step.parent not in payloads:
                        raise Exception("Referenced payload has not been built yet")
                    parent_id = payloads.index(step.parent) + 1
                fixture_steps.append(
                    step.to_fixture_payload_build(
                        next_id,
                        parent_id,
                    )
                )
                payloads.append(step)
            else:
                raise Exception(f"Unsupported step type: {step}")

        return PayloadBuildingFixture(
            fork=network_info,
            genesis=genesis.header,
            pre=pre,
            config=FixtureConfig(
                fork=network_info,
                blob_schedule=FixtureBlobSchedule.from_blob_schedule(fork.blob_schedule()),
            ),
            steps=fixture_steps,
            engine_forkchoice_updated_version=fork.engine_forkchoice_updated_version(),
            engine_get_payload_version=fork.engine_get_payload_version(),
            engine_new_payload_version=fork.engine_new_payload_version(),
        )

    def generate(
        self,
        request: pytest.FixtureRequest,
        t8n: TransitionTool,
        fork: Fork,
        fixture_format: FixtureFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseFixture:
        """Generate the PayloadBuildingFixture fixture."""
        if fixture_format == PayloadBuildingFixture:
            return self.make_fixture(fork, eips, slow=is_slow_test(request))

        raise Exception(f"Unknown fixture format: {fixture_format}")

    def execute(
        self,
        *,
        fork: Fork,
        execute_format: ExecuteFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseExecute:
        """Generate the list of test fixtures."""
        raise Exception(f"Unsupported execute format: {execute_format}")


PayloadBuildingTestSpec = Callable[[str], Generator[PayloadBuildingTest, None, None]]
PayloadBuildingTestFiller = Type[PayloadBuildingTest]
