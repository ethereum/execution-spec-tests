"""
abstract: Tests [EIP-4762: Statelessness gas cost changes]
(https://eips.ethereum.org/EIPS/eip-4762)
    Tests for [EIP-4762: Statelessness gas cost changes]
    (https://eips.ethereum.org/EIPS/eip-4762).
"""

import pytest

from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTestFiller,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "storage_slot_accesses",
    [
        [0],
        [1000],
        [0, 1],
        [0, 1000],
        [1000, 1000],
    ],
    ids=[
        "in_account_header",
        "outside_account_header",
        "two_in_same_branch",
        "two_in_different_branch",
        "cold_plus_warm_cost",
    ],
)
def test_sload(blockchain_test: BlockchainTestFiller, fork: str, storage_slot_accesses):
    """
    Test SLOAD witness.
    """
    exp_witness = None  # TODO(verkle)
    _sload(blockchain_test, fork, storage_slot_accesses, exp_witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "gas_limit",
    [
        "TBD",
        "TBD",
    ],
    ids=[
        "insufficient_for_subtree_edit_cost",
        "insufficient_for_chunk_edit_cost",
    ],
)
def test_sload_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str, gas_limit):
    """
    Test SLOAD with insufficient gas.
    """
    exp_witness = None  # TODO(verkle)
    _sload(blockchain_test, fork, [0], exp_witness, gas_limit=gas_limit)


def _sload(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    storage_slot_accesses,
    exp_witness,
    gas_limit=1_000_000,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    code = bytes()
    for slot in storage_slot_accesses:
        code += Op.SLOAD(slot)

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(
            storage={0: 0xAA, 1000: 0xBB},
            code=code,
        ),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=TestAddress2,
        gas_limit=gas_limit,
        gas_price=10,
    )
    blocks = [Block(txs=[tx])]

    # TODO(verkle): define witness assertion
    witness_keys = ""

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness_keys=witness_keys,
    )
