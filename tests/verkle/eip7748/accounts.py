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

# List of addressed ordered by MPT tree key.
accounts = [
    # 03601462093b5945d1676df093446790fd31b20e7b12a2e8e5e09d068109616b
    Address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"),
    # 1fe26fd0b8a197e7b85ed1ead2b52700041c5d465673aa744f3afc4704f83c03
    Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0d"),
    # 257f371320e4696a5debc64a489e651fc4565eb07ce0e4d2ce5b6d5b1896d89a
    Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0f"),
    # 6a7fc6037f7a0dca7004c2cd41d87bfd929be7eb0d31903b238839e8e7aaf897
    Address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0a"),
    # 85174d7e61a36094fc9b58640ad245d4ab61d888699f3659137171ff2910b6cb
    Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0e"),
    # b4102152d5f5995b7a017c9db0e186028190faafa4326ac1ecfb2bc817c423c9
    Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf05"),
    # e72525e3842ed775ed5c52ffc1520247deae64a217fcb3fb3ddbe59ffeb5949c
    Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf03"),
]


class AccountConfig:
    def __init__(self, code_length: int, storage_slot_count: int):
        self.code_length = code_length
        self.storage_slots_count = storage_slot_count


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "account_configs",
    [
        # [AccountConfig(0, 0)],
        # [AccountConfig(0, 0), AccountConfig(0, 0)],
        [AccountConfig(0, 0), AccountConfig(0, 0), AccountConfig(0, 0)],
        # [AccountConfig(15, 1)],
    ],
    ids=[
        # "One EOA",
        # "Two EOAs",
        "Three EOAs",
        # "Small contract"
    ],
)
@pytest.mark.parametrize(
    "fill_first_block, stride",
    [
        (False, 3),
        # (True, 3),
    ],
)
def test_conversions(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    stride: int,
):
    """
    Test conversion cases.
    """
    conversion_units = 0
    pre_state = {}
    if fill_first_block:
        for i in range(stride):
            conversion_units += 1
            pre_state[accounts[i]] = Account(balance=100 + 1000 * i)

    for i, account_config in enumerate(account_configs, start=len(pre_state)):
        storage = {}
        for j in range(account_config.storage_slots_count):
            conversion_units += 1
            storage[j] = j

        pre_state[accounts[i]] = Account(
            balance=100 + 1000 * i,
            code=Op.JUMPDEST * account_config.code_length,
            storage=storage,
        )
        conversion_units += 1 + math.ceil(account_config.code_length / 31)

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
