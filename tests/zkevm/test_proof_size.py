"""
A series of stress tests that assess the ability of a specific
opcode or precompile to process large proofs in a block.

Large proofs are created by deploying contracts with
maximum allowed bytecode.

Then, a pacman contract (ᗧ•••) consumes the maximum possible number of
proofs in a block with a given gas limit using an opcode or precompile.
"""

from dataclasses import dataclass
from typing import Callable

import pytest

from ethereum_test_tools import (
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Environment,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

##############################
#                            #
#          Config            #
#                            #
##############################
MAX_CODE_SIZE = 24 * 1024  # 24 KiB
GAS_LIMITS = [30_000_000, 60_000_000, 100_000_000, 300_000_000]


@dataclass
class Consumer:
    """
    Consumer configuration for eating proofs.
    Each consumer has a specific gas appetite and bytecode.
    """

    opcode: Op
    """The opcode this consumer uses to eat proofs."""
    gas_cost: int
    """The gas appetite for consuming a single proof."""
    generate_bytecode: Callable[[Address], Bytecode]
    """A lambda function that generates the bytecode for the eating proof."""

    def __str__(self) -> str:
        """Str repr."""
        return f"{self.opcode}"

    def create_pacman(self, pre: Alloc, gas_limit: int) -> Address:
        """
        Generate a pacman contract that ingests proofs using this opcode.
        ᗧ•••  nom nom nom.
        """
        proof_count = (gas_limit - 21_000) // self.gas_cost
        proof_count = 5  # TODO: REMOVE THIS LIMIT

        # Generate proofs
        proofs = [
            pre.deploy_contract(code=Op.JUMPDEST * (MAX_CODE_SIZE - 11) + Op.PUSH10(i))
            for i in range(proof_count)
        ]

        # Generate bytecode using the opcode's configuration
        code = sum(self.generate_bytecode(proof) for proof in proofs)
        if not code:
            raise ValueError("Generated code is empty")

        return pre.deploy_contract(code=code)


CONSUMERS = [
    Consumer(
        opcode=Op.EXTCODEHASH,
        gas_cost=2603,  # PUSH20[3] + EXTCODEHASH[2600]
        generate_bytecode=lambda proof: Op.EXTCODEHASH(proof),
    ),
    Consumer(
        opcode=Op.EXTCODESIZE,
        gas_cost=2603,  # PUSH20[3] + EXTCODESIZE[2600]
        generate_bytecode=lambda proof: Op.EXTCODESIZE(proof),
    ),
]


#############################
#                            #
#       Test Cases           #
#                            #
##############################
@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("gas_limit", GAS_LIMITS)
@pytest.mark.parametrize("consumer", CONSUMERS, ids=str)
def test_via_opcode(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    gas_limit: int,
    consumer: Consumer,
):
    """Test zkEVM proof size limits using a specific opcode."""
    tx = Transaction(
        to=consumer.create_pacman(pre, gas_limit),
        gas_limit=gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
        data=[],
        value=0,
    )

    blockchain_test(
        env=Environment(gas_limit=gas_limit),
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )

    # TODO: Assert that ingestion cost is computed correctly
