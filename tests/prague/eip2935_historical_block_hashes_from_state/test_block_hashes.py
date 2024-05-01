"""
abstract: Tests [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
    Test [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
"""  # noqa: E501

from enum import unique
from typing import Dict, List

import pytest

from ethereum_test_tools import Account, Address, Block, BlockchainTestFiller, Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Storage, TestAddress, Transaction

from .spec import Spec, ref_spec_2935

REFERENCE_SPEC_GIT_PATH = ref_spec_2935.git_path
REFERENCE_SPEC_VERSION = ref_spec_2935.version

FORK_TIMESTAMP = 15_000


@pytest.mark.parametrize(
    "blocks_before_fork",
    [1, 2],
)
@pytest.mark.parametrize("blocks_after_fork", [2])
@pytest.mark.valid_at_transition_to("Prague")
def test_block_hashes_at_transition(
    blockchain_test: BlockchainTestFiller,
    blocks_before_fork: int,
    blocks_after_fork: int,
):
    """
    Test the fork transition and that the block hashes of previous blocks, even blocks
    before the fork, are included in the state at the moment of the transition.
    """
    # Fork happens at timestamp 15_000, and genesis counts as a block before fork.
    blocks: List[Block] = []
    assert blocks_before_fork >= 1 and blocks_before_fork < FORK_TIMESTAMP

    code_before_block_address = Address(0x200)
    code_before_block = b""
    code_before_block_storage: Dict[int, int] = {}
    for i in range(1, blocks_before_fork):
        # On the last block before the fork, BLOCKHASH must return values for the last 256 block
        # but not for the blocks before that.
        if i > Spec.BLOCKHASH_OLD_WINDOW:
            oldest_block = i - Spec.BLOCKHASH_OLD_WINDOW
            block_outside_window = i - Spec.BLOCKHASH_OLD_WINDOW - 1
            code_before_block = Op.SSTORE(
                0, Op.ISZERO(Op.BLOCKHASH(block_outside_window))
            ) + Op.SSTORE(1, Op.ISZERO(Op.BLOCKHASH(oldest_block)))
        else:
            # Simply check the oldest block (Genesis) which should be available
            oldest_block = 0
            code_before_block = Op.SSTORE(0, 1) + Op.SSTORE(
                1, Op.ISZERO(Op.BLOCKHASH(oldest_block))
            )
        code_before_block_storage = {0: 1, 1: 0}
        tx = Transaction(
            to=code_before_block_address,
            gas_limit=10_000_000,
        )
        blocks.append(Block(timestamp=i, txs=[tx]))

    # Add the blocks after the fork
    for i in range(FORK_TIMESTAMP, FORK_TIMESTAMP + blocks_after_fork):
        blocks.append(Block(timestamp=i))

    pre = {
        TestAddress: Account(balance=10_000_000_000),
        code_before_block_address: Account(code=code_before_block, nonce=1),
    }

    post: Dict[Address, Account] = {
        code_before_block_address: Account(storage=code_before_block_storage),
    }

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        blocks=blocks,
        post=post,
    )
