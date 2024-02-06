"""
abstract: Tests [EIP-6800: Ethereum state using a unified verkle tree](https://eips.ethereum.org/EIPS/eip-6800)
    Test state tree conversion from MPT [EIP-6800: Ethereum state using a unified verkle tree](https://eips.ethereum.org/EIPS/eip-6800)

"""  # noqa: E501

from itertools import count
from typing import List, Mapping

import pytest

from ethereum_test_tools import Account, Address, Block, BlockchainTestFiller, Environment, Hash
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Storage, TestAddress, Transaction

code_address = Address(0x100)

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6800.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.fixture
def pre() -> Mapping:  # noqa: D103
    return {
        TestAddress: Account(balance=10**40),
        code_address: Account(
            nonce=1,
            balance=1,
            code=Op.SSTORE(Op.CALLDATALOAD(0), Op.CALLDATALOAD(32)),
        ),
    }


@pytest.mark.valid_at_transition_to("Prague")
def test_verkle_from_mpt_conversion(
    blockchain_test: BlockchainTestFiller,
    pre: Mapping[str, Account],
):
    """
    Perform MCOPY operations using different offsets and lengths:
      - Zero inputs
      - Memory rewrites (copy from and to the same location)
      - Memory overwrites (copy from and to different locations)
      - Memory extensions (copy to a location that is out of bounds)
      - Memory clear (copy from a location that is out of bounds)
    """
    nonce = count()
    block_count = 64
    tx_count = 64
    blocks: List[Block] = []
    code_storage = Storage()
    for _ in range(block_count):
        txs: List[Transaction] = []
        for t in range(tx_count):
            storage_value = 2**256 - t - 1
            storage_key = code_storage.store_next(storage_value)
            txs.append(
                Transaction(
                    nonce=next(nonce),
                    to=code_address,
                    data=Hash(storage_key) + Hash(storage_value),
                    gas_limit=100_000,
                )
            )
        blocks.append(Block(txs=txs))
    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post={
            code_address: Account(
                nonce=1,
                balance=1,
                code=Op.SSTORE(Op.CALLDATALOAD(0), Op.CALLDATALOAD(32)),
                storage=code_storage,
            ),
        },
        blocks=blocks,
    )
