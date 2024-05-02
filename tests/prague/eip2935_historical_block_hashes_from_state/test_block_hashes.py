"""
abstract: Tests [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
    Test [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
"""  # noqa: E501

from itertools import count
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
    [
        pytest.param(1, id="fork_at_1"),
        pytest.param(Spec.BLOCKHASH_OLD_WINDOW, id="fork_at_BLOCKHASH_OLD_WINDOW"),
        pytest.param(Spec.BLOCKHASH_OLD_WINDOW + 1, id="fork_at_BLOCKHASH_OLD_WINDOW_plus_1"),
        pytest.param(
            Spec.HISTORY_SERVE_WINDOW + 1,
            id="fork_at_HISTORY_SERVE_WINDOW_plus_1",
            marks=pytest.mark.slow,
        ),
    ],
)
@pytest.mark.valid_at_transition_to("Prague")
def test_block_hashes_history_at_transition(
    blockchain_test: BlockchainTestFiller,
    blocks_before_fork: int,
):
    """
    Test the fork transition and that the block hashes of previous blocks, even blocks
    before the fork, are included in the state at the moment of the transition.
    """
    # Fork happens at timestamp 15_000, and genesis counts as a block before fork.
    blocks: List[Block] = []
    assert blocks_before_fork >= 1 and blocks_before_fork < FORK_TIMESTAMP

    pre = {TestAddress: Account(balance=10_000_000_000)}
    post: Dict[Address, Account] = {}
    tx_nonce = count(0)

    current_code_address = 0x10000
    for i in range(1, blocks_before_fork):
        txs: List[Transaction] = []
        if i == blocks_before_fork - 1:
            # On the last block before the fork, BLOCKHASH must return values for the last 256
            # blocks but not for the blocks before that.
            # And HISTORY_STORAGE_ADDRESS should be empty.
            code = b""
            storage = Storage()
            # Check the first block outside the window
            if i > Spec.BLOCKHASH_OLD_WINDOW:
                # We can check that blocks before the window are not available
                block_outside_window = i - Spec.BLOCKHASH_OLD_WINDOW - 1

                # Check using BLOCKHASH, must be zero
                code += Op.SSTORE(
                    storage.store_next(1), Op.ISZERO(Op.BLOCKHASH(block_outside_window))
                )

                # Check calling the HISTORY_STORAGE_ADDRESS, must be zero
                code += Op.MSTORE(0, block_outside_window)
                code += Op.POP(Op.CALL(Op.GAS, Spec.HISTORY_STORAGE_ADDRESS, 0, 0, 32, 0, 32))
                code += Op.RETURNDATACOPY(0, 0, 32)
                code += Op.SSTORE(storage.store_next(1), Op.ISZERO(Op.MLOAD(0)))

            else:
                # No block outside the window
                pass

            # Check the oldest block inside the window
            if i > Spec.BLOCKHASH_OLD_WINDOW:
                oldest_block = i - Spec.BLOCKHASH_OLD_WINDOW
            else:
                oldest_block = 0

            # Check using BLOCKHASH, must be greater than zero
            code += Op.SSTORE(storage.store_next(1), Op.GT(Op.BLOCKHASH(oldest_block), 0))

            # Check calling the HISTORY_STORAGE_ADDRESS, must be zero
            code += Op.MSTORE(0, oldest_block)
            code += Op.POP(Op.CALL(Op.GAS, Spec.HISTORY_STORAGE_ADDRESS, 0, 0, 32, 0, 32))
            code += Op.RETURNDATACOPY(0, 0, 32)
            code += Op.SSTORE(storage.store_next(1), Op.ISZERO(Op.MLOAD(0)))

            txs.append(
                Transaction(
                    to=current_code_address,
                    gas_limit=10_000_000,
                    nonce=next(tx_nonce),
                )
            )
            pre[Address(current_code_address)] = Account(code=code, nonce=1)
            post[Address(current_code_address)] = Account(storage=storage)
            current_code_address += 0x100
        blocks.append(Block(timestamp=i, txs=txs))

    # Add the fork block
    current_block_number = len(blocks) + 1
    txs = []
    # On the block after the fork, BLOCKHASH must return values for the last
    # Spec.HISTORY_SERVE_WINDOW blocks.
    # And HISTORY_STORAGE_ADDRESS should be also serve the same values.
    code = b""
    storage = Storage()
    if current_block_number > Spec.HISTORY_SERVE_WINDOW:
        # We can check that blocks before the window are not available
        block_outside_window = current_block_number - Spec.HISTORY_SERVE_WINDOW - 1

        # Check using BLOCKHASH, must be zero
        code += Op.SSTORE(storage.store_next(1), Op.ISZERO(Op.BLOCKHASH(block_outside_window)))

        # Check calling the HISTORY_STORAGE_ADDRESS, must be zero
        code += Op.MSTORE(0, block_outside_window)
        code += Op.POP(Op.CALL(Op.GAS, Spec.HISTORY_STORAGE_ADDRESS, 0, 0, 32, 0, 32))
        code += Op.RETURNDATACOPY(0, 0, 32)
        code += Op.SSTORE(storage.store_next(1), Op.ISZERO(Op.MLOAD(0)))
    else:
        # No block outside the window
        pass

    if current_block_number > Spec.HISTORY_SERVE_WINDOW:
        oldest_block = current_block_number - Spec.HISTORY_SERVE_WINDOW
    else:
        oldest_block = 0

    # Check using BLOCKHASH, must be greater than zero
    code += Op.SSTORE(storage.store_next(1), Op.GT(Op.BLOCKHASH(oldest_block), 0))

    # Check calling the HISTORY_STORAGE_ADDRESS
    code += Op.MSTORE(0, oldest_block)
    code += Op.POP(Op.CALL(Op.GAS, Spec.HISTORY_STORAGE_ADDRESS, 0, 0, 32, 0, 32))
    code += Op.RETURNDATACOPY(0, 0, 32)
    # Must be greater than zero
    code += Op.SSTORE(storage.store_next(1), Op.GT(Op.MLOAD(0), 0))
    # Must be equal to the value returned by BLOCKHASH
    code += Op.SSTORE(storage.store_next(1), Op.EQ(Op.MLOAD(0), Op.BLOCKHASH(oldest_block)))

    txs.append(
        Transaction(
            to=current_code_address,
            gas_limit=10_000_000,
            nonce=next(tx_nonce),
        )
    )
    pre[Address(current_code_address)] = Account(code=code, nonce=1)
    post[Address(current_code_address)] = Account(storage=storage)
    current_code_address += 0x100

    blocks.append(Block(timestamp=FORK_TIMESTAMP, txs=txs))

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        blocks=blocks,
        post=post,
    )
