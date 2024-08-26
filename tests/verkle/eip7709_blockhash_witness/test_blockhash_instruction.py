"""
abstract: Tests [EIP-7709: Read BLOCKHASH from storage and update cost]
(https://eips.ethereum.org/EIPS/eip-7709)
    Tests for [EIP-7709: Read BLOCKHASH from storage and update cost]
    (https://eips.ethereum.org/EIPS/eip-7709).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7709.md"
REFERENCE_SPEC_VERSION = "TODO"

# TODO(verkle): to be confirmed
blockhash_system_contract_address = Address("0xa4690f0ed0d089faa1e0ad94c8f1b4a2fd4b0734")
HISTORY_STORAGE_ADDRESS = 8192
BLOCKHASH_OLD_WINDOW = 256
block_number = 1000


@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "block_num_target",
    [
        block_number + 10,
        block_number,
        block_number - 1,
        block_number - BLOCKHASH_OLD_WINDOW,
        block_number - BLOCKHASH_OLD_WINDOW - 1,
    ],
    ids=[
        "future_block",
        "current_block",
        "previous_block",
        "last_supported_block",
        "too_old_block",
    ],
)
def test_blockhash(blockchain_test: BlockchainTestFiller, block_num_target: int):
    """
    Test BLOCKHASH witness.
    """
    _blockhash(blockchain_test, block_num_target)


@pytest.mark.valid_from("Verkle")
def test_blockhash_insufficient_gas(blockchain_test: BlockchainTestFiller):
    """
    Test BLOCKHASH with insufficient gas.
    """
    _blockhash(blockchain_test, block_number - 1, gas_limit=21_042, fail=True)


def _blockhash(
    blockchain_test: BlockchainTestFiller,
    block_num_target: int,
    gas_limit=1_000_000,
    fail=False,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=Op.BLOCKHASH(block_num_target)),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )

    # Validate that pre, fee recipient, & blockhash system contract are present in the witness
    witness_check = WitnessCheck()

    blocks = [Block(txs=[tx], witness_check=witness_check)]
    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
    )
