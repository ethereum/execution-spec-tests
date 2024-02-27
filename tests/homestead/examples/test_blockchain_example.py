"""
Opcodes Blockchain Test Tutorial Example
"""

from typing import Dict, List

import pytest

from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    TestAddress,
    Transactions,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op


@pytest.fixture
def contract_address() -> Address:
    return Address(0x100)


@pytest.fixture
def contract_code() -> bytes:
    return Op.SSTORE(Op.SLOAD(0), Op.NUMBER) + Op.SSTORE(0, Op.ADD(0, Op.SLOAD(0)))


@pytest.fixture
def pre(contract_address: Address, contract_code: bytes) -> Dict:
    return {
        TestAddress: Account(balance=10**9),
        contract_address: Account(
            balance=10**9,
            code=contract_code,
        ),
    }


@pytest.fixture
def txs_per_block() -> List[int]:
    return [2, 0, 4, 8, 0, 0, 20, 1, 50]


@pytest.fixture
def blocks(contract_address: Address, txs_per_block: List[int], fork: Fork) -> List[Block]:
    blocks = []
    for txs_count in txs_per_block:
        blocks.append(
            Block(
                txs=Transactions(
                    limit=txs_count,
                    ty=0x0,
                    to=contract_address,
                    gas_limit=100000,
                    gas_price=10,
                    protected=False if fork in [Frontier, Homestead] else True,
                )
            )
        )
    return blocks


@pytest.fixture
def post(contract_address: Address, txs_per_block: List[int]) -> Dict:
    storage = {0: sum(txs_per_block) + 1}
    next_slot = 1
    for blocknum in range(len(txs_per_block)):
        for _ in range(txs_per_block[blocknum]):
            storage[next_slot] = blocknum + 1
            next_slot = next_slot + 1
    return {contract_address: Account(storage=storage)}


@pytest.mark.valid_from("Homestead")
def test_block_number(
    blockchain_test: BlockchainTestFiller, pre: Dict, blocks: List[Block], post: Dict
):
    """
    Test the NUMBER opcode in different blocks
    """
    blockchain_test(pre=pre, post=post, blocks=blocks)
