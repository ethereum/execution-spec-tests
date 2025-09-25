"""Ethereum benchmark test spec definition and filler."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Dict, Generator, List, Sequence, Type

import pytest
from pydantic import ConfigDict, Field

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
from ethereum_test_vm import Bytecode
from ethereum_test_vm.opcodes import Opcodes as Op

from .base import BaseTest
from .blockchain import Block, BlockchainTest


@dataclass(kw_only=True)
class BenchmarkCodeGenerator(ABC):
    """Abstract base class for generating benchmark bytecode."""

    attack_block: Bytecode
    setup: Bytecode = field(default_factory=Bytecode)

    @abstractmethod
    def deploy_contracts(self, pre: Alloc, fork: Fork) -> None:
        """Deploy any contracts needed for the benchmark."""
        ...

    @abstractmethod
    def generate_transaction(self, pre: Alloc, gas_limit: int, fork: Fork) -> Transaction:
        """Generate a transaction with the specified gas limit."""
        ...

    def generate_repeated_code(
        self, repeated_code: Bytecode, setup: Bytecode, fork: Fork
    ) -> Bytecode:
        """
        Calculate the maximum number of iterations that
        can fit in the code size limit.
        """
        assert len(repeated_code) > 0, "repeated_code cannot be empty"
        max_code_size = fork.max_code_size()

        overhead = len(setup) + len(Op.JUMPDEST) + len(Op.JUMP(len(setup)))
        available_space = max_code_size - overhead
        max_iterations = available_space // len(repeated_code)

        code = setup + Op.JUMPDEST + repeated_code * max_iterations + Op.JUMP(len(setup))
        self._validate_code_size(code, fork)

        return code

    def _validate_code_size(self, code: Bytecode, fork: Fork) -> None:
        """Validate that the generated code fits within size limits."""
        if len(code) > fork.max_code_size():
            raise ValueError(
                f"Generated code size {len(code)} exceeds maximum allowed size "
                f"{fork.max_code_size()}"
            )


class BenchmarkTest(BaseTest):
    """Test type designed specifically for benchmark test cases."""

    model_config = ConfigDict(extra="forbid")

    pre: Alloc
    post: Alloc = Field(default_factory=Alloc)
    tx: Transaction | None = None
    blocks: List[Block] | None = None
    block_exception: (
        List[TransactionException | BlockException] | TransactionException | BlockException | None
    ) = None
    env: Environment = Field(default_factory=Environment)
    expected_benchmark_gas_used: int | None = None
    gas_benchmark_value: int = Field(default_factory=lambda: int(Environment().gas_limit))
    code_generator: BenchmarkCodeGenerator | None = None

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
        """
        Return the parameter name used in pytest
        to select this spec type.
        """
        return "benchmark_test"

    @classmethod
    def discard_fixture_format_by_marks(
        cls,
        fixture_format: FixtureFormat,
        fork: Fork,
        markers: List[pytest.Mark],
    ) -> bool:
        """
        Discard a fixture format from filling if the
        appropriate marker is used.
        """
        if "blockchain_test_only" in [m.name for m in markers]:
            return fixture_format != BlockchainFixture
        if "blockchain_test_engine_only" in [m.name for m in markers]:
            return fixture_format != BlockchainEngineFixture
        return False

    def get_genesis_environment(self, fork: Fork) -> Environment:
        """Get the genesis environment for this benchmark test."""
        return self.env

    def split_transaction(self, tx: Transaction, gas_limit_cap: int | None) -> List[Transaction]:
        """
        Split a transaction that exceeds the gas
        limit cap into multiple transactions.
        """
        if gas_limit_cap is None:
            tx.gas_limit = HexNumber(self.gas_benchmark_value)
            return [tx]

        if gas_limit_cap >= self.gas_benchmark_value:
            tx.gas_limit = HexNumber(self.gas_benchmark_value)
            return [tx]

        num_splits = math.ceil(self.gas_benchmark_value / gas_limit_cap)
        remaining_gas = self.gas_benchmark_value

        split_transactions = []
        for i in range(num_splits):
            split_tx = tx.model_copy()
            split_tx.gas_limit = HexNumber(remaining_gas if i == num_splits - 1 else gas_limit_cap)
            remaining_gas -= gas_limit_cap
            split_tx.nonce = HexNumber(tx.nonce + i)
            split_transactions.append(split_tx)

        return split_transactions

    def generate_blocks_from_code_generator(self, fork: Fork) -> List[Block]:
        """Generate blocks using the code generator."""
        if self.code_generator is None:
            raise Exception("Code generator is not set")

        self.code_generator.deploy_contracts(self.pre, fork)
        gas_limit = fork.transaction_gas_limit_cap() or self.gas_benchmark_value
        benchmark_tx = self.code_generator.generate_transaction(self.pre, gas_limit, fork)

        execution_txs = self.split_transaction(benchmark_tx, gas_limit)
        execution_block = Block(txs=execution_txs)

        return [execution_block]

    def generate_blockchain_test(self, fork: Fork) -> BlockchainTest:
        """Create a BlockchainTest from this BenchmarkTest."""
        set_props = [
            name
            for name, val in [
                ("code_generator", self.code_generator),
                ("blocks", self.blocks),
                ("tx", self.tx),
            ]
            if val is not None
        ]

        if len(set_props) != 1:
            raise ValueError(
                f"Exactly one must be set, but got {len(set_props)}: {', '.join(set_props)}"
            )

        if self.code_generator is not None:
            generated_blocks = self.generate_blocks_from_code_generator(fork)
            return BlockchainTest.from_test(
                base_test=self,
                genesis_environment=self.env,
                pre=self.pre,
                post=self.post,
                blocks=generated_blocks,
            )
        elif self.blocks is not None:
            return BlockchainTest.from_test(
                base_test=self,
                genesis_environment=self.env,
                pre=self.pre,
                post=self.post,
                blocks=self.blocks,
            )
        elif self.tx is not None:
            gas_limit = fork.transaction_gas_limit_cap() or self.gas_benchmark_value

            transactions = self.split_transaction(self.tx, gas_limit)

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
