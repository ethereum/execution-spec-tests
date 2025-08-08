"""Ethereum benchmark test spec definition and filler."""

from typing import Callable, ClassVar, Dict, Generator, List, Optional, Sequence, Type

import pytest
from pydantic import Field

from ethereum_clis import TransitionTool
from ethereum_test_base_types import HexNumber
from ethereum_test_exceptions import BlockException, TransactionException
from ethereum_test_execution import (
    BaseExecute,
    ExecuteFormat,
    LabeledExecuteFormat,
    TransactionPost,
)
from ethereum_test_fixtures import (
    BaseFixture,
    BlockchainEngineFixture,
    BlockchainEngineXFixture,
    BlockchainFixture,
    FixtureFormat,
    LabeledFixtureFormat,
)
from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Environment, Transaction

from .base import BaseTest
from .blockchain import Block, BlockchainTest


class BenchmarkTest(BaseTest):
    """Test type designed specifically for benchmark test cases."""

    pre: Alloc
    post: Alloc
    tx: Optional[Transaction] = None
    blocks: Optional[List[Block]] = None
    block_exception: (
        List[TransactionException | BlockException] | TransactionException | BlockException | None
    ) = None
    env: Environment = Field(default_factory=Environment)
    expected_benchmark_gas_used: int | None = None

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = [
        BlockchainFixture,
        BlockchainEngineFixture,
        BlockchainEngineXFixture,
    ]

    supported_execute_formats: ClassVar[Sequence[LabeledExecuteFormat]] = [
        LabeledExecuteFormat(
            TransactionPost,
            "benchmark_test",
            "An execute test derived from a benchmark test",
        ),
    ]

    supported_markers: ClassVar[Dict[str, str]] = {
        "blockchain_test_engine_only": "Only generate a blockchain test engine fixture",
        "blockchain_test_only": "Only generate a blockchain test fixture",
    }

    @classmethod
    def pytest_parameter_name(cls) -> str:
        """Return the parameter name used in pytest to select this spec type."""
        return "benchmark_test"

    @classmethod
    def discard_fixture_format_by_marks(
        cls,
        fixture_format: FixtureFormat,
        fork: Fork,
        markers: List[pytest.Mark],
    ) -> bool:
        """Discard a fixture format from filling if the appropriate marker is used."""
        if "blockchain_test_only" in [m.name for m in markers]:
            return fixture_format != BlockchainFixture
        if "blockchain_test_engine_only" in [m.name for m in markers]:
            return fixture_format != BlockchainEngineFixture
        return False

    def get_genesis_environment(self, fork: Fork) -> Environment:
        """Get the genesis environment for this benchmark test."""
        return self.env

    def split_transaction(self, tx: Transaction, gas_limit_cap: int | None) -> List[Transaction]:
        """Split a transaction that exceeds the gas limit cap into multiple transactions."""
        if (gas_limit_cap is None) or (tx.gas_limit <= gas_limit_cap):
            return [tx]

        total_gas = int(self.expected_benchmark_gas_used or self.env.gas_limit)
        print(f"total_gas: {total_gas}")
        num_splits = total_gas // gas_limit_cap

        split_transactions = []
        for i in range(num_splits):
            split_tx = tx.model_copy()
            total_gas -= gas_limit_cap
            split_tx.gas_limit = HexNumber(total_gas if i == num_splits - 1 else gas_limit_cap)
            split_tx.nonce = HexNumber(tx.nonce + i)
            split_transactions.append(split_tx)

        return split_transactions

    def generate_blockchain_test(self, fork: Fork) -> BlockchainTest:
        """Create a BlockchainTest from this BenchmarkTest."""
        if self.blocks is not None:
            return BlockchainTest.from_test(
                base_test=self,
                genesis_environment=self.env,
                pre=self.pre,
                post=self.post,
                blocks=self.blocks,
            )
        elif self.tx is not None:
            gas_limit_cap = fork.transaction_gas_limit_cap()

            transactions = self.split_transaction(self.tx, gas_limit_cap)

            blocks = [Block(txs=transactions)]

            return BlockchainTest.from_test(
                base_test=self,
                pre=self.pre,
                post=self.post,
                blocks=blocks,
                genesis_environment=self.env,
            )
        else:
            raise ValueError("Cannot create BlockchainTest without transactions or blocks")

    def generate(
        self,
        t8n: TransitionTool,
        fork: Fork,
        fixture_format: FixtureFormat,
    ) -> BaseFixture:
        """Generate the blockchain test fixture."""
        self.check_exception_test(exception=self.tx.error is not None if self.tx else False)
        if fixture_format in BlockchainTest.supported_fixture_formats:
            return self.generate_blockchain_test(fork=fork).generate(
                t8n=t8n, fork=fork, fixture_format=fixture_format
            )
        else:
            raise Exception(f"Unsupported fixture format: {fixture_format}")

    def execute(
        self,
        *,
        fork: Fork,
        execute_format: ExecuteFormat,
    ) -> BaseExecute:
        """Execute the benchmark test by sending it to the live network."""
        if execute_format == TransactionPost:
            return TransactionPost(
                blocks=[[self.tx]],
                post=self.post,
            )
        raise Exception(f"Unsupported execute format: {execute_format}")


BenchmarkTestSpec = Callable[[str], Generator[BenchmarkTest, None, None]]
BenchmarkTestFiller = Type[BenchmarkTest]
