"""Benchmark code generator classes for creating optimized bytecode patterns."""

from abc import ABC, abstractmethod
from typing import Optional

from ethereum_test_forks import Fork
from ethereum_test_tools import Alloc, Bytecode, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op


class BenchmarkCodeGenerator(ABC):
    """Abstract base class for generating benchmark bytecode."""

    def __init__(
        self,
        fork: Fork,
        attack_block: Bytecode,
        setup: Optional[Bytecode] = None,
    ):
        """Initialize with fork, attack block, and optional setup bytecode."""
        self.fork = fork
        self.setup = setup or Bytecode()
        self.attack_block = attack_block

    @abstractmethod
    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate a transaction with the specified gas limit."""
        pass

    def generate_repeated_code(self, repeated_code: Bytecode, setup: Bytecode) -> Bytecode:
        """Calculate the maximum number of iterations that can fit in the code size limit."""
        max_code_size = self.fork.max_code_size()

        overhead = len(Op.JUMPDEST) + len(Op.JUMP(len(setup)))
        available_space = max_code_size - overhead
        max_iterations = available_space // len(repeated_code) if len(repeated_code) > 0 else 0

        code = setup + Op.JUMPDEST + repeated_code * max_iterations + Op.JUMP(len(setup))

        self._validate_code_size(code)

        return code

    def _validate_code_size(self, code: Bytecode) -> None:
        """Validate that the generated code fits within size limits."""
        if len(code) > self.fork.max_code_size():
            raise ValueError(
                f"Generated code size {len(code)} exceeds maximum allowed size "
                f"{self.fork.max_code_size()}"
            )


class JumpLoopGenerator(BenchmarkCodeGenerator):
    """Generates bytecode that loops execution using JUMP operations."""

    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate transaction with looping bytecode pattern."""
        # Benchmark Test Structure:
        # setup + JUMPDEST + attack + attack + ... + attack + JUMP(setup_length)

        code = self.generate_repeated_code(self.attack_block, self.setup)

        return Transaction(
            to=pre.deploy_contract(code=code),
            gas_limit=self.fork.transaction_gas_limit_cap() or 30_000_000,
            sender=pre.fund_eoa(),
        )


class ExtCallGenerator(BenchmarkCodeGenerator):
    """Generates bytecode that fills the contract to maximum allowed code size."""

    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate transaction with maximal code size coverage."""
        # Benchmark Test Structure:
        # There are two contracts:
        # 1. The target contract that executes certain operation but not loop (e.g. PUSH)
        # 2. The loop contract that calls the target contract in a loop
        #
        # attack = POP(STATICCALL(GAS, target_contract_address, 0, 0, 0, 0))
        # setup + JUMPDEST + attack + attack + ... + attack + JUMP(setup_lengt)
        # This could optimize the gas consumption and increase the cycle count.

        max_stack_height = self.fork.max_stack_height()

        target_contract_address = pre.deploy_contract(code=self.attack_block * max_stack_height)

        code_sequence = Op.POP(Op.STATICCALL(Op.GAS, target_contract_address, 0, 0, 0, 0))

        code = self.generate_repeated_code(code_sequence, Bytecode())

        return Transaction(
            to=pre.deploy_contract(code=code),
            gas_limit=self.fork.transaction_gas_limit_cap() or 30_000_000,
            sender=pre.fund_eoa(),
        )
