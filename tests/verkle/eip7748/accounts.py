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

accounts = sorted([Address(i) for i in range(0, 50)], key=lambda x: x.keccak256())


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
        [AccountConfig(0, 0)] * 7,
        [AccountConfig(15, 2)],
        [AccountConfig(31 * 2 + 1, 3)],  # 3 code-chunks + 3 slots + account data = 7
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
    [
        False,
        True,
    ],
)
def test_conversions(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
):
    """
    Test conversion cases.
    """
    stride = 7
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
            storage[j] = j + 1

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
