"""
abstract: Tests [EIP-7748: State conversion to Verkle Tree]
(https://eips.ethereum.org/EIPS/eip-7748)
    Tests for [EIP-7748: State conversion to Verkle Tree]
    (https://eips.ethereum.org/EIPS/eip-7748).
"""

import pytest
import math
import sys

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7748.md"
REFERENCE_SPEC_VERSION = "TODO"

stride = 7
accounts = sorted([Address(i) for i in range(0, 100)], key=lambda x: x.keccak256())


class AccountConfig:
    def __init__(self, code_length: int, storage_slot_count: int):
        self.code_length = code_length
        self.storage_slots_count = storage_slot_count


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        [AccountConfig(0, 0)],
        [AccountConfig(0, 0)] * 2,
        [AccountConfig(0, 0)] * stride,
        [AccountConfig(15, 2)],
        [AccountConfig(31 * 2 + 1, 3)],  # 3 code-chunks + 3 slots + account data = stride
        [AccountConfig(0, 0), AccountConfig(15, 2)],
        [
            AccountConfig(0, 0),
            AccountConfig(31 + 1, 3),
        ],
        [
            AccountConfig(15, 2),
            AccountConfig(0, 0),
        ],
        [
            AccountConfig(31 + 1, 3),
            AccountConfig(0, 0),
        ],
        [
            AccountConfig(5, 1),
            AccountConfig(8, 1),
        ],
        [
            AccountConfig(5, 2),
            AccountConfig(8, 1),
        ],
    ],
    ids=[
        "EOA",
        "EOAs under-fit",
        "EOAs perfect-fit",
        "Contract under-fit",
        "Contract perfect-fit",
        "EOA and Contract under-fit",
        "EOA and Contract perfect-fit",
        "Contract and EOA under-fit",
        "Contract and EOA perfect-fit",
        "Contract and Contract under-fit",
        "Contract and Contract perfect-fit",
    ],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [False, True],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [False, True],
)
def test_non_partial(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test non-partial account conversions.
    """
    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        # No prefix
        [AccountConfig(31 * 2 + 1, stride + 2)],
        [AccountConfig(31 * 2 + 1, stride + 1)],
        [AccountConfig(31 + 2 + 1, stride)],
        # EOA prefix
        [AccountConfig(0, 0), AccountConfig(42, -1 + stride + 2)],
        [AccountConfig(0, 0), AccountConfig(42, -1 + stride + 1)],
        [AccountConfig(0, 0), AccountConfig(42, -1 + stride)],
        # Contract prefix
        [AccountConfig(10, 1), AccountConfig(42, -3 + stride + 2)],
        [AccountConfig(10, 1), AccountConfig(42, -3 + stride + 1)],
        [AccountConfig(10, 1), AccountConfig(42, -3 + stride)],
    ],
    ids=[
        "No prefix & boundary at two storage slots before finishing storage trie",
        "No prefix & boundary at one storage slot before finishing storage trie",
        "No prefix & boundary matching exactly the end of the storage trie",
        "EOA prefix & boundary at two storage slots before finishing storage trie",
        "EOA prefix & boundary at one storage slot before finishing storage trie",
        "EOA prefix & boundary matching exactly the end of the storage trie",
        "Contract prefix & boundary at two storage slots before finishing storage trie",
        "Contract prefix & boundary at one storage slot before finishing storage trie",
        "Contract prefix & boundary matching exactly the end of the storage trie",
    ],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [False, True],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [False, True],
)
def test_partial(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test partial account conversions.
    """
    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        [AccountConfig(31 * (stride + 10) + 1, 4)],
        [AccountConfig(31 * (stride + 3), 1), AccountConfig(0, 0)],
    ],
    ids=[
        "Stride overflow",
        "Stride overflow followed by EOA",
    ],
)
@pytest.mark.parametrize(
    "fill_first_block",
    [False, True],
)
@pytest.mark.parametrize(
    "fill_last_block",
    [False, True],
)
def test_codechunks_stride_overflow(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    """
    Test code-chunks stride overflow.
    """
    _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


def _generic_conversion(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    conversion_units = 0
    pre_state = {}
    account_idx = 0
    if fill_first_block:
        for i in range(stride):
            conversion_units += 1
            pre_state[accounts[account_idx]] = Account(balance=100 + 1000 * i)
            account_idx += 1

    for i, account_config in enumerate(account_configs):
        storage = {}
        for j in range(account_config.storage_slots_count):
            conversion_units += 1
            storage[j] = j + 1

        pre_state[accounts[account_idx]] = Account(
            balance=100 + 1000 * i,
            nonce=i,
            code=Op.JUMPDEST * account_config.code_length,
            storage=storage,
        )
        account_idx += 1

        conversion_units += 1  # Account basic data
        num_code_chunks = math.ceil(account_config.code_length / 31)
        # Code is always converted in one go, but it counts for stride quota usage
        conversion_units += min(num_code_chunks, stride - conversion_units % stride)

    if fill_last_block:
        for i in range((-conversion_units) % stride + stride):
            conversion_units += 1
            pre_state[accounts[account_idx]] = Account(balance=100 + 1000 * i)
            account_idx += 1

    _state_conversion(blockchain_test, pre_state, stride, math.ceil(conversion_units / stride))


# @pytest.mark.skip("stride config not supported yet")
# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "fcb, stride, num_expected_blocks",
#     [
#         (True, 1, 2),
#         (True, 2, 1),
#         (False, 1, 1),
#         (False, 2, 1),
#     ],
# )
# def test_empty_account(
#     blockchain_test: BlockchainTestFiller,
#     fcb: bool,
#     stride: int,
#     num_expected_blocks: int,
# ):
#     """
#     Test EIP-161 accounts.
#     """
#     pre_state = {}
#     if not fcb:
#         pre_state[Account0] = Account(balance=1000)

#     # Empty account (EIP-161)
#     pre_state[Account1] = Account(
#         balance=0,
#         nonce=0,
#         storage={0: 0x1, 1: 0x2},
#     )

#     pre_state[Account2] = Account(balance=1001)

#     _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


# @pytest.mark.skip("stride config not supported yet")
# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "fcb, stride, num_expected_blocks",
#     [
#         (True, 1, 2),
#         (True, 2, 1),
#         (False, 1, 1),
#     ],
# )
# def test_last_conversion_block(
#     blockchain_test: BlockchainTestFiller,
#     fcb: bool,
#     stride: int,
#     num_expected_blocks: int,
# ):
#     """
#     Test last conversion block scenario.
#     """
#     pre_state = {}
#     if not fcb:
#         pre_state[Account0] = Account(balance=1000)

#     # Empty account (EIP-161)
#     pre_state[Account1] = Account(
#         balance=0,
#         nonce=0,
#         storage={0: 0x1, 1: 0x2},
#     )

#     _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


def _state_conversion(
    blockchain_test: BlockchainTestFiller,
    pre_state: dict[Address, Account],
    stride: int,
    num_blocks: int,
):
    # TODO: test library should allow passing stride
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
    )

    blocks: list[Block] = []
    for i in range(num_blocks):
        blocks.append(Block(txs=[]))

    # TODO: witness assertion
    # TODO: see if possible last block switch to finished conversion

    blockchain_test(
        genesis_environment=env,
        pre=pre_state,
        post=pre_state.copy(),
        blocks=blocks,
    )
