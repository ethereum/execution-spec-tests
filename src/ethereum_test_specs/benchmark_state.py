"""Ethereum benchmark state test spec definition and filler."""

import math
from pprint import pprint
from typing import Callable, ClassVar, Generator, List, Sequence, Type

from pydantic import ConfigDict

from ethereum_clis import TransitionTool
from ethereum_test_base_types import HexNumber
from ethereum_test_execution import (
    BaseExecute,
    ExecuteFormat,
    LabeledExecuteFormat,
    TransactionPost,
)
from ethereum_test_fixtures import (
    BaseFixture,
    FixtureFormat,
    LabeledFixtureFormat,
    StateFixture,
)
from ethereum_test_fixtures.common import FixtureBlobSchedule
from ethereum_test_fixtures.state import (
    FixtureConfig,
    FixtureEnvironment,
    FixtureForkPost,
    FixtureTransaction,
)
from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Environment, Transaction

from .base import BaseTest, OpMode
from .blockchain import Block, BlockchainTest
from .debugging import print_traces
from .helpers import verify_transactions


class BenchmarkStateTest(BaseTest):
    """Test type designed specifically for benchmark state test cases with full verification."""

    pre: Alloc
    post: Alloc
    tx: Transaction
    gas_benchmark_value: int
    env: Environment
    chain_id: int = 1

    model_config = ConfigDict(arbitrary_types_allowed=True)

    supported_fixture_formats: ClassVar[Sequence[FixtureFormat | LabeledFixtureFormat]] = [
        StateFixture,
    ] + [
        LabeledFixtureFormat(
            fixture_format,
            f"{fixture_format.format_name}_from_benchmark_state_test",
            f"A {fixture_format.format_name} generated from a benchmark_state_test",
        )
        for fixture_format in BlockchainTest.supported_fixture_formats
    ]

    supported_execute_formats: ClassVar[Sequence[LabeledExecuteFormat]] = [
        LabeledExecuteFormat(
            TransactionPost,
            "benchmark_state_test_with_verification",
            "An execute test derived from a benchmark state test with verification",
        ),
    ]

    def split_transaction(self, tx: Transaction, gas_limit_cap: int | None) -> List[Transaction]:
        """Split a transaction that exceeds the gas limit cap into multiple transactions."""
        if (gas_limit_cap is None) or (tx.gas_limit <= gas_limit_cap):
            return [tx]

        total_gas = int(tx.gas_limit)
        num_splits = math.ceil(total_gas / gas_limit_cap)

        split_transactions = []
        remaining_gas = total_gas
        for i in range(num_splits):
            split_tx = tx.model_copy()
            split_tx.gas_limit = HexNumber(min(gas_limit_cap, remaining_gas))
            split_tx.nonce = HexNumber(tx.nonce + i)
            split_transactions.append(split_tx)
            remaining_gas -= gas_limit_cap

        return split_transactions

    def make_benchmark_state_test_fixture(
        self,
        t8n: TransitionTool,
        fork: Fork,
    ) -> StateFixture:
        """Create a fixture from the benchmark state test definition with full verification."""
        # We can't generate a state test fixture that names a transition fork,
        # so we get the fork at the block number and timestamp of the state test
        fork = fork.fork_at(self.env.number, self.env.timestamp)

        env = self.env.set_fork_requirements(fork)
        tx = self.tx.with_signature_and_sender(keep_secret_key=True)
        pre_alloc = Alloc.merge(
            Alloc.model_validate(fork.pre_allocation()),
            self.pre,
        )

        # Verification 1: Check for empty accounts
        if empty_accounts := pre_alloc.empty_accounts():
            raise Exception(f"Empty accounts in pre state: {empty_accounts}")

        transition_tool_output = t8n.evaluate(
            transition_tool_data=TransitionTool.TransitionToolData(
                alloc=pre_alloc,
                txs=[tx],
                env=env,
                fork=fork,
                chain_id=self.chain_id,
                reward=0,  # Reward on state tests is always zero
                blob_schedule=fork.blob_schedule(),
                state_test=True,
            ),
            debug_output_path=self.get_next_transition_tool_output_path(),
            slow_request=self.is_tx_gas_heavy_test(),
        )

        # Verification 2: Post-allocation verification
        try:
            self.post.verify_post_alloc(transition_tool_output.alloc)
        except Exception as e:
            print_traces(t8n.get_traces())
            raise e

        # Verification 3: Transaction verification
        try:
            verify_transactions(
                txs=[tx],
                result=transition_tool_output.result,
                transition_tool_exceptions_reliable=t8n.exception_mapper.reliable,
            )
        except Exception as e:
            print_traces(t8n.get_traces())
            pprint(transition_tool_output.result)
            pprint(transition_tool_output.alloc)
            raise e

        # Verification 4: Benchmark gas validation
        if self._operation_mode == OpMode.BENCHMARKING:
            expected_benchmark_gas_used = self.gas_benchmark_value
            gas_used = int(transition_tool_output.result.gas_used)
            assert expected_benchmark_gas_used is not None, "gas_benchmark_value is not set"
            assert gas_used == expected_benchmark_gas_used, (
                f"gas_used ({gas_used}) does not match gas_benchmark_value "
                f"({expected_benchmark_gas_used})"
                f", difference: {gas_used - expected_benchmark_gas_used}"
            )

        return StateFixture(
            env=FixtureEnvironment(**env.model_dump(exclude_none=True)),
            pre=pre_alloc,
            post={
                fork: [
                    FixtureForkPost(
                        state_root=transition_tool_output.result.state_root,
                        logs_hash=transition_tool_output.result.logs_hash,
                        tx_bytes=tx.rlp(),
                        expect_exception=tx.error,
                        state=transition_tool_output.alloc,
                    )
                ]
            },
            transaction=FixtureTransaction.from_transaction(tx),
            config=FixtureConfig(
                blob_schedule=FixtureBlobSchedule.from_blob_schedule(fork.blob_schedule()),
                chain_id=self.chain_id,
            ),
        )

    def generate_blockchain_test(self, fork: Fork) -> BlockchainTest:
        """Create a BlockchainTest from this BenchmarkStateTestWithVerification."""
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

    def generate(
        self,
        t8n: TransitionTool,
        fork: Fork,
        fixture_format: FixtureFormat,
    ) -> BaseFixture:
        """Generate the test fixture."""
        self.check_exception_test(exception=self.tx.error is not None)
        if fixture_format in BlockchainTest.supported_fixture_formats:
            return self.generate_blockchain_test(fork=fork).generate(
                t8n=t8n, fork=fork, fixture_format=fixture_format
            )
        elif fixture_format == StateFixture:
            return self.make_benchmark_state_test_fixture(t8n, fork)

        raise Exception(f"Unknown fixture format: {fixture_format}")

    def execute(
        self,
        *,
        fork: Fork,
        execute_format: ExecuteFormat,
    ) -> BaseExecute:
        """Execute the benchmark state test by sending it to the live network."""
        if execute_format == TransactionPost:
            return TransactionPost(
                blocks=[[self.tx]],
                post=self.post,
            )
        raise Exception(f"Unsupported execute format: {execute_format}")


BenchmarkStateTestFiller = Type[BenchmarkStateTest]
BenchmarkStateTestSpec = Callable[[str], Generator[BenchmarkStateTest, None, None]]
