"""
Benchmark code generator classes for creating
optimized bytecode patterns.
"""

from ethereum_test_base_types import Address
from ethereum_test_forks import Fork
from ethereum_test_specs.benchmark import BenchmarkCodeGenerator
from ethereum_test_types import Alloc, Transaction
from ethereum_test_vm import Bytecode
from ethereum_test_vm.opcodes import Opcodes as Op


class JumpLoopGenerator(BenchmarkCodeGenerator):
    """Generates bytecode that loops execution using JUMP operations."""

    def deploy_contracts(self, pre: Alloc, fork: Fork) -> Address:
        """Deploy the looping contract."""
        # Benchmark Test Structure:
        # setup + JUMPDEST + attack + attack + ... + cleanup + JUMP(setup_length)
        code = self.generate_repeated_code(self.attack_block, self.setup, self.cleanup, fork)
        self._contract_address = pre.deploy_contract(code=code)
        return self._contract_address

    def generate_transaction(self, pre: Alloc, gas_limit: int, fork: Fork) -> Transaction:
        """Generate transaction that executes the looping contract."""
        if not hasattr(self, "_contract_address"):
            self.deploy_contracts(pre, fork)

        return Transaction(
            to=self._contract_address,
            gas_limit=gas_limit,
            sender=pre.fund_eoa(),
        )


class ExtCallGenerator(BenchmarkCodeGenerator):
    """
    Generates bytecode that fills the contract to
    maximum allowed code size.
    """

    def deploy_contracts(self, pre: Alloc, fork: Fork) -> Address:
        """Deploy both target and caller contracts."""
        # Benchmark Test Structure:
        # There are two contracts:
        # 1. The target contract that executes certain operation
        #    but not loop (e.g. PUSH)
        # 2. The loop contract that calls the target contract in a loop

        max_iterations = min(
            fork.max_stack_height(), fork.max_code_size() // len(self.attack_block)
        )

        # Deploy target contract that contains the actual attack block
        self._target_contract_address = pre.deploy_contract(
            code=self.setup + self.attack_block * max_iterations
        )

        # Create caller contract that repeatedly calls the target contract
        # attack = POP(
        #             STATICCALL(GAS, target_contract_address, 0, 0, 0, 0)
        #          )
        #
        # setup + JUMPDEST + attack + attack + ... + attack +
        # JUMP(setup_length)
        code_sequence = Op.POP(Op.STATICCALL(Op.GAS, self._target_contract_address, 0, 0, 0, 0))

        caller_code = self.generate_repeated_code(code_sequence, Bytecode(), self.cleanup, fork)
        self._contract_address = pre.deploy_contract(code=caller_code)
        return self._contract_address

    def generate_transaction(self, pre: Alloc, gas_limit: int, fork: Fork) -> Transaction:
        """Generate transaction that executes the caller contract."""
        if not hasattr(self, "_contract_address"):
            self.deploy_contracts(pre, fork)

        return Transaction(
            to=self._contract_address,
            gas_limit=gas_limit,
            sender=pre.fund_eoa(),
        )
