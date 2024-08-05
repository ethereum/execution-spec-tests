"""
abstract: Tests [EIP-6800: Ethereum state using a unified verkle tree]
(https://eips.ethereum.org/EIPS/eip-6800)
    Tests for [EIP-6800: Ethereum state using a unified verkle tree]
    (https://eips.ethereum.org/EIPS/eip-6800).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    Transaction,
    compute_create_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6800.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

precompile_address = Address("0x04")


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "slot_num",
    [
        0,
        63,
        64,
        255,
        513,
        2**256 - 1,
    ],
    ids=[
        "header_zero",
        "header_limit",
        "first_non_header_zero",
        "first_non_header_limit",
        "other_non_header",
        "biggest",
    ],
)
def test_storage_slot_write(blockchain_test: BlockchainTestFiller, fork: str, slot_num):
    """
    Test that storage slot writes work as expected.
    """
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        data=Op.SSTORE(slot_num, 0x42),
    )
    blocks = [Block(txs=[tx])]

    contract_address = compute_create_address(TestAddress, tx.nonce)

    post = {
        contract_address: Account(
            storage={
                slot_num: 0x42,
            },
        ),
    }

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
