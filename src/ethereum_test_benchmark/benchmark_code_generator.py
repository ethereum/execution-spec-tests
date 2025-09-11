"""Benchmark code generator classes for creating optimized bytecode patterns."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ethereum_test_forks import Fork
from ethereum_test_types import Alloc, Transaction
from ethereum_test_vm import Bytecode
from ethereum_test_vm.opcode import Opcodes as Op


@dataclass
class BenchmarkCodeGenerator(ABC):
    """Abstract base class for generating benchmark bytecode."""

    fork: Fork
    attack_block: Bytecode
    setup: Bytecode = field(default_factory=Bytecode)

    @abstractmethod
    def deploy_contracts(self, pre: Alloc) -> None:
        """Deploy any contracts needed for the benchmark."""
        pass

    @abstractmethod
    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate a transaction with the specified gas limit."""
        pass

    def generate_repeated_code(self, repeated_code: Bytecode, setup: Bytecode) -> Bytecode:
        """Calculate the maximum number of iterations that can fit in the code size limit."""
        assert len(repeated_code) > 0, "repeated_code cannot be empty"
        max_code_size = self.fork.max_code_size()

        overhead = len(setup) + len(Op.JUMPDEST) + len(Op.JUMP(len(setup)))
        available_space = max_code_size - overhead
        max_iterations = available_space // len(repeated_code)

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


@dataclass
class JumpLoopGenerator(BenchmarkCodeGenerator):
    """Generates bytecode that loops execution using JUMP operations."""

    def deploy_contracts(self, pre: Alloc) -> None:
        """Deploy the looping contract."""
        # Benchmark Test Structure:
        # setup + JUMPDEST + attack + attack + ... + attack + JUMP(setup_length)
        code = self.generate_repeated_code(self.attack_block, self.setup)
        self._contract_address = pre.deploy_contract(code=code)

    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate transaction that executes the looping contract."""
        if not hasattr(self, "_contract_address"):
            raise ValueError("deploy_contracts must be called before generate_transaction")

        return Transaction(
            to=self._contract_address,
            gas_limit=gas_limit,
            sender=pre.fund_eoa(),
        )


@dataclass
class ExtCallGenerator(BenchmarkCodeGenerator):
    """Generates bytecode that fills the contract to maximum allowed code size."""

    def deploy_contracts(self, pre: Alloc) -> None:
        """Deploy both target and caller contracts."""
        # Benchmark Test Structure:
        # There are two contracts:
        # 1. The target contract that executes certain operation but not loop (e.g. PUSH)
        # 2. The loop contract that calls the target contract in a loop

        max_stack_height = self.fork.max_stack_height()

        # Deploy target contract that contains the actual attack block
        self._target_contract_address = pre.deploy_contract(
            code=self.attack_block * max_stack_height
        )

        # Create caller contract that repeatedly calls the target contract
        # attack = POP(STATICCALL(GAS, target_contract_address, 0, 0, 0, 0))
        # setup + JUMPDEST + attack + attack + ... + attack + JUMP(setup_length)
        code_sequence = Op.POP(Op.STATICCALL(Op.GAS, self._target_contract_address, 0, 0, 0, 0))

        caller_code = self.generate_repeated_code(code_sequence, Bytecode())
        self._contract_address = pre.deploy_contract(code=caller_code)

    def generate_transaction(self, pre: Alloc, gas_limit: int) -> Transaction:
        """Generate transaction that executes the caller contract."""
        if not hasattr(self, "_contract_address"):
            raise ValueError("deploy_contracts must be called before generate_transaction")

        return Transaction(
            to=self._contract_address,
            gas_limit=gas_limit,
            sender=pre.fund_eoa(),
        )
