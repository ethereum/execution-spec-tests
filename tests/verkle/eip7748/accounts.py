"""
abstract: Tests [EIP-7748: State conversion to Verkle Tree]
(https://eips.ethereum.org/EIPS/eip-7748)
    Tests for [EIP-7748: State conversion to Verkle Tree]
    (https://eips.ethereum.org/EIPS/eip-7748).
"""

import pytest

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
# 03601462093b5945d1676df093446790fd31b20e7b12a2e8e5e09d068109616b
Account0 = Address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b")
# 0e195438d9f92eb191032b5f660d42a22255c9c417248f092c1f83f3a36b29ba
Account1 = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0e")
# 6a7fc6037f7a0dca7004c2cd41d87bfd929be7eb0d31903b238839e8e7aaf897
Account2 = Address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0a")
# 6a8737909ea3e92b0d47328d70aff338c526832b32362eca8692126c1f399846
Account3 = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0d")
# d3bd43970708294fd4d78893c4e7c2fed43c8cd505e9c9516e1f11e79f574598
Account4 = Address("0xd94f5374fce5edbc8e2a8697c15331677e6ebf0f")


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "stride, num_expected_blocks",
    [
        (1, 3),
        (2, 2),
        (3, 1),
    ],
)
def test_eoa(blockchain_test: BlockchainTestFiller, stride: int, num_expected_blocks: int):
    """
    Test only EOA account conversion.
    """
    pre_state = {
        Account0: Account(balance=1000),
        Account1: Account(balance=2000),
        Account2: Account(balance=3000),
    }
    _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "contract_length",
    [
        0,
        1,
        128 * 31,
        130 * 31,
    ],
    ids=[
        "empty",
        "in_header",
        "header_perfect_fit",
        "bigger_than_header",
    ],
)
@pytest.mark.parametrize(
    "fcb, stride, num_expected_blocks",
    [
        (True, 1, 6),
        (True, 2, 3),
        (True, 3, 2),
        (True, 4, 2),
        (True, 5, 2),
        (True, 6, 1),
        (False, 1, 3),
        (False, 2, 2),
        (False, 3, 1),
    ],
)
def test_full_contract(
    blockchain_test: BlockchainTestFiller,
    contract_length: int,
    fcb: bool,
    stride: int,
    num_expected_blocks: int,
):
    """
    Test contract account full/partial migration cases.
    """
    pre_state = {}
    if not fcb:
        pre_state[Account0] = Account(balance=1000)
        pre_state[Account1] = Account(balance=1001)
        pre_state[Account2] = Account(balance=1002)

    pre_state[Account3] = Account(
        balance=2000,
        code=Op.STOP * contract_length,
        storage={0: 0x1, 1: 0x2},
    )

    _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "fcb, stride, num_expected_blocks",
    [
        (True, 1, 2),
        (True, 2, 1),
        (False, 1, 1),
        (False, 2, 1),
    ],
)
def test_empty_account(
    blockchain_test: BlockchainTestFiller,
    fcb: bool,
    stride: int,
    num_expected_blocks: int,
):
    """
    Test EIP-161 accounts.
    """
    pre_state = {}
    if not fcb:
        pre_state[Account0] = Account(balance=1000)

    # Empty account (EIP-161)
    pre_state[Account1] = Account(
        balance=0,
        nonce=0,
        storage={0: 0x1, 1: 0x2},
    )

    pre_state[Account2] = Account(balance=1001)

    _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "fcb, stride, num_expected_blocks",
    [
        (True, 1, 2),
        (True, 2, 1),
        (False, 1, 1),
    ],
)
def test_last_conversion_block(
    blockchain_test: BlockchainTestFiller,
    fcb: bool,
    stride: int,
    num_expected_blocks: int,
):
    """
    Test last conversion block scenario.
    """
    pre_state = {}
    if not fcb:
        pre_state[Account0] = Account(balance=1000)

    # Empty account (EIP-161)
    pre_state[Account1] = Account(
        balance=0,
        nonce=0,
        storage={0: 0x1, 1: 0x2},
    )

    _state_conversion(blockchain_test, pre_state, stride, num_expected_blocks)


def _state_conversion(
    blockchain_test: BlockchainTestFiller,
    pre_state: dict[Address, Account],
    stride: int,
    num_expected_blocks: int,
):
    # TODO: test library should allow passing stride
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
    )

    blocks: list[Block] = []
    for i in range(num_expected_blocks):
        blocks.append(Block(txs=[]))

    # TODO: witness assertion
    # TODO: see if possible last block switch to finished conversion

    blockchain_test(
        genesis_environment=env,
        pre=pre_state,
        post=pre_state.copy(),
        blocks=blocks,
    )
