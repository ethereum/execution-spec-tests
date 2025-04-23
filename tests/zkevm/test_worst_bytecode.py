"""
abstract: Tests for zkEVMs
    Tests for zkEVMs.

Tests for zkEVMs worst-cases scenarios.
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Alloc, Block, BlockchainTestFiller, Environment, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "TODO"
REFERENCE_SPEC_VERSION = "TODO"

MAX_CONTRACT_SIZE = 24 * 1024
GAS_LIMIT = 36_000_000
MAX_NUM_CONTRACT_CALLS = (GAS_LIMIT - 21_000) // (3 + 2600 + 2)


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
def test_worst_bytecode(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    fork: Fork,
    num_called_contracts: int,
):
    """Test a block execution calling contracts with the maximum size of bytecode."""
    env = Environment(gas_limit=GAS_LIMIT)

    contract_addrs = []
    for i in range(num_called_contracts):
        contract_addrs.append(
            pre.deploy_contract(code=Op.JUMPDEST * (MAX_CONTRACT_SIZE - 1 - 10) + Op.PUSH10(i))
        )

    attack_code = sum(
        [(Op.EXTCODESIZE(contract_addrs[i]) + Op.POP) for i in range(num_called_contracts)]
    )
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
