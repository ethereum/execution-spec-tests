"""
Ethereum transaction test spec definition and filler.
"""

from typing import Callable, ClassVar, Generator, List, Optional, Type

import pytest

from ethereum_clis import TransitionTool
from ethereum_test_execution import BaseExecute, ExecuteFormat, TransactionPost
from ethereum_test_fixtures import BaseFixture, FixtureFormat, TransactionFixture
from ethereum_test_fixtures.transaction import Fixture, FixtureResult
from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Transaction

from .base import BaseTest

TARGET_BLOB_GAS_PER_BLOCK = 393216


class TransactionTest(BaseTest):
    """
    Filler type that tests the transaction over the period of a single block.
    """

    tx: Transaction
    pre: Alloc | None = None

    supported_fixture_formats: ClassVar[List[FixtureFormat]] = [
        TransactionFixture,
    ]
    supported_execute_formats: ClassVar[List[ExecuteFormat]] = [
        TransactionPost,
    ]

    def make_transaction_test_fixture(
        self,
        fork: Fork,
        eips: Optional[List[int]] = None,
    ) -> Fixture:
        """
        Create a fixture from the transaction test definition.
        """
        if self.tx.error is not None:
            result = FixtureResult(
                exception=self.tx.error,
                hash=None,
                intrinsic_gas=0,
                sender=None,
            )
        else:
            result = FixtureResult(
                exception=None,
                hash=self.tx.hash,
                intrinsic_gas=self.tx.intrinsic_gas(fork),
                sender=self.tx.sender,
            )

        return Fixture(
            result={
                fork.blockchain_test_network_name(): result,
            },
            transaction=self.tx.rlp,
        )

    def generate(
        self,
        request: pytest.FixtureRequest,
        t8n: TransitionTool,
        fork: Fork,
        fixture_format: FixtureFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseFixture:
        """
        Generate the TransactionTest fixture.
        """
        if fixture_format == TransactionFixture:
            return self.make_transaction_test_fixture(fork, eips)

        raise Exception(f"Unknown fixture format: {fixture_format}")

    def execute(
        self,
        *,
        fork: Fork,
        execute_format: ExecuteFormat,
        eips: Optional[List[int]] = None,
    ) -> BaseExecute:
        """
        Execute the transaction test by sending it to the live network.
        """
        if execute_format == TransactionPost:
            return TransactionPost(
                transactions=[self.tx],
                post={},
            )
        raise Exception(f"Unsupported execute format: {execute_format}")


TransactionTestSpec = Callable[[str], Generator[TransactionTest, None, None]]
TransactionTestFiller = Type[TransactionTest]
