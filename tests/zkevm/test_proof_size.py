"""
A series of stress tests that assess the ability of a specific
opcode or precompile to process large proofs in a block.

A large proof is created by deploying a contract with
maximum allowed bytecode.

This proof is then "ingested" by an opcode or precompile.

These tests first compute the "ingestion cost" for the proof.
Next, they attempt to perform the maximum number of possible
ingestions in a block.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Alloc, Block, BlockchainTestFiller, Environment, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"


##############################
#                            #
#          Config            #
#                            #
##############################
GAS_LIMIT = 36_000_000

KiB = 1024
CONTRACT_BYTECODE_MAX_SIZE = 24 * KiB
MAX_NUM_CONTRACT_CALLS = (GAS_LIMIT - 21_000) // (3 + 2600)


@pytest.mark.zkevm
@pytest.mark.valid_from("Cancun")
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
    num_called_contracts: int,
):
    """Test zkEVM proof size limits using a specific opcode."""
    env = Environment(gas_limit=GAS_LIMIT)

    contract_addrs = []
    for i in range(num_called_contracts):
        code = Op.JUMPDEST * (CONTRACT_BYTECODE_MAX_SIZE - 1 - 10) + Op.PUSH10(i)
        contract_addrs.append(pre.deploy_contract(code=code))

    attack_code = sum([Op.EXTCODESIZE(contract_addrs[i]) for i in range(num_called_contracts)])
    attack_contract = pre.deploy_contract(code=attack_code)

    tx = Transaction(
        to=attack_contract,
        gas_limit=GAS_LIMIT,
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
