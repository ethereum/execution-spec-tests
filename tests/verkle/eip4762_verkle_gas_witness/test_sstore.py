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

from ..temp_verkle_helpers import Witness

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

TestAddress2Storage = {0: 0xAA, 1000: 0xBB}


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "storage_slot_writes",
    [
        [(0, 0xFF)],
        [(1000, 0xFF)],
        [(0, 0xFF), (1, 0xFF)],
        [(0, 0xFF), (1000, 0xFF)],
        [(5000, 0xFF)],
        [(1000, 0x00)],
        [(5000, 0x00)],
        [(1000, 0xFF), (1000, 0xFE)],
    ],
    ids=[
        "subreeedit_chunkedit_in_account_header",
        "subreeedit_chunkedit_outside_account_header",
        "two_in_same_branch_with_fill_cost",
        "two_different_subtreeedit_cost_and_no_fill_cost",
        "fill_and_subtree_edit_cost",
        "non_zero_slot_value_reset",
        "zero_slot_write_zero_value",
        "warm_write",
    ],
)
def test_sstore(blockchain_test: BlockchainTestFiller, fork: str, storage_slot_writes):
    """
    Test SSTORE witness.
    """
    witness = Witness()
    for sstore in storage_slot_writes:
        witness.add_storage_slot(TestAddress2, sstore[0], TestAddress2Storage.get(sstore[0]))

    _sstore(blockchain_test, fork, storage_slot_writes, witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.parametrize(
    "gas_limit, must_be_in_witness",
    [
        ("TBD", False),
        ("TBD", True),
    ],
    ids=[
        "cant_pay_subtree_edit_and_chunk_edit_cost",
        "cant_pay_fill_cost",
    ],
)
def test_sstore_insufficient_gas(
    blockchain_test: BlockchainTestFiller, fork: str, gas_limit: int, must_be_in_witness: bool
):
    """
    Test SSTORE with insufficient gas.
    """
    witness = Witness()
    if must_be_in_witness:
        witness.add_storage_slot(TestAddress2, 5000, None)

    _sstore(
        blockchain_test,
        fork,
        [(5000, 0xFF)],
        witness,
        gas_limit=gas_limit,
        post_state_mutated_slot_count=0,
    )


def _sstore(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    storage_slot_writes: list[tuple[int, int]],
    extra_witness: Witness,
    gas_limit=1_000_000,
    post_state_mutated_slot_count=None,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    code = bytes()
    for slot_write in storage_slot_writes:
        code += Op.SSTORE(slot_write[0], slot_write[1])

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(
            storage=TestAddress2Storage,
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

    postStorage = TestAddress2Storage
    successful_writes = (
        len(storage_slot_writes)
        if post_state_mutated_slot_count is None
        else post_state_mutated_slot_count
    )
    for i in range(successful_writes):
        postStorage[storage_slot_writes[i][0]] = storage_slot_writes[i][1]

    post = {
        TestAddress2: Account(
            code=code,
            storage=postStorage,
        ),
    }

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.add_account_full(TestAddress2, pre[TestAddress2])
    witness.merge(extra_witness)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
        witness=witness,
    )
