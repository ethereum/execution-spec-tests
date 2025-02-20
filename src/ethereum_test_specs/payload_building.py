"""Ethereum payload building test specs."""

from typing import Callable, ClassVar, Generator, List, Optional, Sequence, Type

import pytest
from pydantic import Field

from ethereum_clis import TransitionTool
from ethereum_test_base_types import CamelModel
from ethereum_test_execution import BaseExecute, ExecuteFormat, LabeledExecuteFormat
from ethereum_test_fixtures import (
    BaseFixture,
    FixtureFormat,
    LabeledFixtureFormat,
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
    """
    Expected resulting post allocation of the transaction being included in a block.

    The allocations are expected to be compounded with the expected allocation of previously
    and future included transactions.
    """

    invalidates: List[Transaction] = Field(default_factory=list)
    """
    List of transactions that should be invalidated by this transaction.

    When this transaction is included in a block, none of the transactions in the
    `invalidates` list should be included afterwards (same block or subsequent block).
    """

    def to_fixture_transaction_with_post(self) -> FixtureSendTransactionWithPost:
        """Return FixtureTransaction from a Transaction."""
        signed_self = self.with_signature_and_sender()
        kwargs = signed_self.model_dump()
        kwargs.pop("post")
        kwargs.pop("invalidates")
        return FixtureSendTransactionWithPost(
            **kwargs,
            rlp=signed_self.rlp,
            hash=signed_self.hash,
            post=self.post,
            invalidates=[t.with_signature_and_sender().hash for t in self.invalidates],
        )


class Payload(CamelModel):
    """
    Test step to request the client to build a payload using `engine_forkchoiceUpdated` followed
    by `engine_getPayload`, with a custom sleep duration between the two requests.

    Contains also the verification description that should be performed.
    """

    get_payload_wait_ms: int = 1000
    """
    The number of milliseconds to wait between the `engine_forkchoiceUpdated` and
    `engine_getPayload` requests.
    """
    parent: "Payload | None" = None
    """
    The parent payload that this payload is based on. If None, this value is automatically set to
    the previous payload in the list of payloads.
    """

    def to_fixture_payload_build(
        self,
        payload_id: int,
        parent_payload_id: int,
    ) -> FixturePayloadBuild:
        """Convert a Payload to a FixturePayloadBuild."""
        return FixturePayloadBuild(
            id=payload_id,
            parent_id=parent_payload_id,
            get_payload_wait_ms=self.get_payload_wait_ms,
        )


class PayloadBuildingTest(BaseTest):
    """Spec that verifies block building behavior."""

    pre: Alloc
    chain_id: int = 1
    steps: List[TransactionWithPost | Transaction | Payload]
    genesis_environment: Environment = Field(default_factory=Environment)

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = [
        PayloadBuildingFixture,
    ]
    supported_execute_formats: ClassVar[Sequence[ExecuteFormat | LabeledExecuteFormat]] = []

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
                fixture_step: FixtureSendTransactionWithPost
                if isinstance(step, TransactionWithPost):
                    fixture_step = step.to_fixture_transaction_with_post()
                else:
                    signed_step = step.with_signature_and_sender()
                    fixture_step = FixtureSendTransactionWithPost(
                        **signed_step.model_dump(),
                        rlp=signed_step.rlp,
                        hash=signed_step.hash,
                    )
                fixture_steps.append(fixture_step)

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
