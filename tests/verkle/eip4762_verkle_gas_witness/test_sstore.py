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
    Bytecode,
    Environment,
    TestAddress,
    TestAddress2,
    Transaction,
    WitnessCheck,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.verkle.types import Hash

# TODO(verkle): Update reference spec version
REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4762.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

TestAddress2Storage: dict[int, Hash] = {0: Hash(0xAA), 1000: Hash(0xBB)}


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
def test_sstore(blockchain_test: BlockchainTestFiller, storage_slot_writes):
    """
    Test SSTORE witness.
    """
    witness_check_extra = WitnessCheck()
    for sstore in storage_slot_writes:
        witness_check_extra.add_storage_slot(
            TestAddress2, sstore[0], TestAddress2Storage.get(sstore[0])
        )

    _sstore(blockchain_test, storage_slot_writes, witness_check_extra)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
@pytest.mark.skip("TBD gas limit")
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
    blockchain_test: BlockchainTestFiller, gas_limit: int, must_be_in_witness: bool
):
    """
    Test SSTORE with insufficient gas.
    """
    witness_check_extra = WitnessCheck()
    if must_be_in_witness:
        witness_check_extra.add_storage_slot(TestAddress2, 5000, None)

    _sstore(
        blockchain_test,
        [(5000, 0xFF)],
        witness_check_extra,
        gas_limit=gas_limit,
        post_state_mutated_slot_count=0,
    )


def _sstore(
    blockchain_test: BlockchainTestFiller,
    storage_slot_writes: list[tuple[int, int]],
    witness_check_extra: WitnessCheck,
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
    code = Bytecode()
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

    postStorage = TestAddress2Storage.copy()
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

    witness_check = witness_check_extra
    for address in [TestAddress, TestAddress2, env.fee_recipient]:
        witness_check.add_account_full(
            address=address,
            account=pre.get(address),
        )

    blocks = [
        Block(
            txs=[tx],
            witness_check=witness_check,
        )
    ]

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post=post,
        blocks=blocks,
    )
