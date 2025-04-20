"""
A series of stress tests that assess the ability of a specific
opcode or precompile to process large proofs in a block.

Large proofs are created by deploying contracts with
maximum allowed bytecode.

These proofs are then "ingested" by an opcode or precompile.

First, the tests compute the "ingestion cost" for the proof.
Next, they attempt to ingest the maximum possible number of
proofs in a block with a given gas limit.
"""

from typing import List

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
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
GAS_LIMITS = [
    30_000_000,
]
KiB = 1024
CONTRACT_BYTECODE_MAX_SIZE = 24 * KiB


##############################
#                            #
#       Test Helpers         #
#                            #
##############################
def get_proofs(pre: Alloc, proof_count: int) -> List[Address]:
    """
    Generate a list of proof addresses by deploying contracts
    with maximum allowed bytecode size.
    """
    proofs = []
    for i in range(proof_count):
        code = Op.JUMPDEST * (CONTRACT_BYTECODE_MAX_SIZE - 1 - 10) + Op.PUSH10(i)
        proofs.append(pre.deploy_contract(code=code))
    return proofs


def get_proof_eater(pre: Alloc, proof_count: int) -> Address:
    """Generate a proof eater contract that ingests a given proofs."""
    proofs = get_proofs(pre, proof_count)
    code = sum([Op.EXTCODESIZE(proofs[i]) for i in range(proof_count)])
    return pre.deploy_contract(code=code)


##############################
#                            #
#       Test Cases           #
#                            #
##############################
@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
@pytest.mark.parametrize("gas_limit", GAS_LIMITS)
@pytest.mark.parametrize(
    "num_called_contracts",
    [
        1,
        # 10,
        # MAX_NUM_CONTRACT_CALLS
    ],
)
def test_via_opcode(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    gas_limit: int,
    num_called_contracts: int,
):
    """Test zkEVM proof size limits using a specific opcode."""
    env = Environment(gas_limit=gas_limit)

    # MAX_NUM_CONTRACT_CALLS = (gas_limit - 21_000) // (3 + 2600)

    tx = Transaction(
        to=get_proof_eater(pre, num_called_contracts),
        gas_limit=gas_limit,
        gas_price=10,
        sender=pre.fund_eoa(),
        data=[],
        value=0,
    )

    blockchain_test(
        env=env,
        pre=pre,
        post={},
        blocks=[Block(txs=[tx])],
    )

    # TODO: Assert that ingestion cost is computed correctly
