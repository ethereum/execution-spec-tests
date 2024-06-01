"""
abstract: Tests [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
    Test [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
"""  # noqa: E501

from typing import Dict, List

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Block,
    BlockchainTestFiller,
    Bytecode,
    Environment,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import Storage, Transaction

from .spec import Spec, ref_spec_2935

REFERENCE_SPEC_GIT_PATH = ref_spec_2935.git_path
REFERENCE_SPEC_VERSION = ref_spec_2935.version


def generate_block_check_code(
    block_number: int | None,
    populated_blockhash: bool,
    populated_history_storage_contract: bool,
    storage: Storage,
    check_contract_first: bool = False,
) -> Bytecode:
    """
    Generate EVM code to check that the block hashes are correctly stored in the state.

    Args:
        block_number (int | None): The block number to check (or None to return empty code).
        populated_blockhash (bool): Whether the blockhash should be populated.
        populated_contract (bool): Whether the contract should be populated.
        storage (Storage): The storage object to use.
        check_contract_first (bool): Whether to check the contract first, for slot warming checks.
    """
    if block_number is None:
        # No block number to check
        return Bytecode()

    blockhash_key = storage.store_next(not populated_blockhash)
    contract_key = storage.store_next(not populated_history_storage_contract)

    check_blockhash = Op.SSTORE(blockhash_key, Op.ISZERO(Op.BLOCKHASH(block_number)))
    check_contract = (
        Op.MSTORE(0, block_number)
        + Op.POP(Op.CALL(Op.GAS, Spec.HISTORY_STORAGE_ADDRESS, 0, 0, 32, 0, 32))
        + Op.SSTORE(contract_key, Op.ISZERO(Op.MLOAD(0)))
    )

    if check_contract_first:
        code = check_contract + check_blockhash
    else:
        code = check_blockhash + check_contract

    if populated_history_storage_contract and populated_blockhash:
        # Both values must be equal
        code += Op.SSTORE(storage.store_next(True), Op.EQ(Op.MLOAD(0), Op.BLOCKHASH(block_number)))

    return code


@pytest.mark.parametrize(
    "blocks_before_fork, blocks_after_fork",
    [
        [1, 1],
        [Spec.BLOCKHASH_OLD_WINDOW + 1, 10],
        [Spec.BLOCKHASH_OLD_WINDOW + 1, Spec.BLOCKHASH_OLD_WINDOW + 1],
        pytest.param(
            Spec.BLOCKHASH_OLD_WINDOW + 1,
            Spec.HISTORY_SERVE_WINDOW + 1,
            marks=pytest.mark.slow,
        ),
        pytest.param(
            Spec.HISTORY_SERVE_WINDOW + 1,
            10,
            marks=pytest.mark.slow,
        ),
        pytest.param(
            Spec.HISTORY_SERVE_WINDOW + 1,
            Spec.HISTORY_SERVE_WINDOW + 1,
            marks=pytest.mark.slow,
        ),
    ],
)
@pytest.mark.valid_at_transition_to("Prague")
def test_block_hashes_history_at_transition(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    blocks_before_fork: int,
    blocks_after_fork: int,
):
    """
    Tests that block hashes are stored correctly at the system contract address after the fork
    transition. Block hashes are stored incrementally at the transition until the
    `HISTORY_SERVE_WINDOW` ring buffer is full. Afterwards the oldest block hash is replaced by the
    new one.

    Note: The block hashes before the fork are no longer stored in the contract at the moment of
    the transition.
    """
    blocks: List[Block] = []
    assert blocks_before_fork >= 1 and blocks_before_fork < Spec.FORK_TIMESTAMP

    sender = pre.fund_eoa(10_000_000_000)
    post: Dict[Address, Account] = {}

    for i in range(1, blocks_before_fork):
        txs: List[Transaction] = []
        if i == blocks_before_fork - 1:
            # On the last block before the fork, `BLOCKHASH` must return values for the last 256
            # blocks but not for the blocks before that.
            # And `HISTORY_STORAGE_ADDRESS` should be empty.
            code = Bytecode()
            storage = Storage()

            # Check the last block before blockhash the window
            code += generate_block_check_code(
                block_number=(
                    i - Spec.BLOCKHASH_OLD_WINDOW - 1
                    if i > Spec.BLOCKHASH_OLD_WINDOW
                    else None  # Chain not long enough, no block to check
                ),
                populated_blockhash=False,
                populated_history_storage_contract=False,
                storage=storage,
            )

            # Check the first block inside blockhash the window
            code += generate_block_check_code(
                block_number=(
                    i - Spec.BLOCKHASH_OLD_WINDOW
                    if i > Spec.BLOCKHASH_OLD_WINDOW
                    else 0  # Entire chain is inside the window, check genesis
                ),
                populated_blockhash=True,
                populated_history_storage_contract=False,
                storage=storage,
            )

            code_address = pre.deploy_contract(code)
            txs.append(
                Transaction(
                    to=code_address,
                    gas_limit=10_000_000,
                    sender=sender,
                )
            )
            post[code_address] = Account(storage=storage)
        blocks.append(Block(timestamp=i, txs=txs))

    # Add the fork block
    current_block_number = len(blocks) + 1
    txs = []
    # On the fork block, `BLOCKHASH` must still return values for the last 256 blocks.
    # `HISTORY_STORAGE_ADDRESS` system contract will store the blockhash for this block during
    # block processing, such that its servable on the subsequent blocks after.
    code = Bytecode()
    storage = Storage()

    # Check the last block before the window
    code += generate_block_check_code(
        block_number=(
            current_block_number - Spec.BLOCKHASH_OLD_WINDOW - 1
            if current_block_number > Spec.BLOCKHASH_OLD_WINDOW
            else None  # Chain not long enough, no block to check
        ),
        populated_blockhash=False,
        populated_history_storage_contract=False,
        storage=storage,
    )

    # Check the first block inside the window
    code += generate_block_check_code(
        block_number=(
            current_block_number - Spec.BLOCKHASH_OLD_WINDOW
            if current_block_number > Spec.BLOCKHASH_OLD_WINDOW
            else 0  # Entire chain is inside the window, check genesis
        ),
        populated_blockhash=True,
        populated_history_storage_contract=False,
        storage=storage,
    )

    code_address = pre.deploy_contract(code)
    txs.append(
        Transaction(
            to=code_address,
            gas_limit=10_000_000,
            sender=sender,
        )
    )
    post[code_address] = Account(storage=storage)

    blocks.append(Block(timestamp=Spec.FORK_TIMESTAMP, txs=txs))

    # Add blocks after the fork transition to gradually fill up the `HISTORY_SERVE_WINDOW`
    for i in range(1, blocks_after_fork + 1):
        current_block_number += 1
        txs = []
        # On these blocks, `BLOCKHASH` will still return values for the last 256 blocks, and
        # `HISTORY_STORAGE_ADDRESS` should now serve values for the previous blocks in the new
        # fork.
        code = Bytecode()
        storage = Storage()

        # Check that each block can return previous blockhashes within `BLOCKHASH_OLD_WINDOW``
        for j in range(1, min(i, Spec.BLOCKHASH_OLD_WINDOW) + 1):
            code += generate_block_check_code(
                block_number=(current_block_number - j),
                populated_blockhash=True,
                populated_history_storage_contract=True,
                storage=storage,
            )

        # Check that each block can return previous blockhashes within `HISTORY_SERVE_WINDOW`
        for j in range(Spec.BLOCKHASH_OLD_WINDOW + 1, min(i, Spec.HISTORY_SERVE_WINDOW) + 1):
            code += generate_block_check_code(
                block_number=(current_block_number - j),
                populated_blockhash=False,
                populated_history_storage_contract=True,
                storage=storage,
            )

        code_address = pre.deploy_contract(code)
        txs.append(
            Transaction(
                to=code_address,
                gas_limit=10_000_000,
                sender=sender,
            )
        )
        post[code_address] = Account(storage=storage)

        blocks.append(Block(timestamp=Spec.FORK_TIMESTAMP + 0x0C, txs=txs))

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        blocks=blocks,
        post=post,
    )
