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
    "storage_slot_accesses",
    [
        [0],
        [1000],
        [0, 1],
        [0, 1000],
        [1000, 1000],
        [5042],
    ],
    ids=[
        "in_account_header",
        "outside_account_header",
        "two_in_same_branch",
        "two_in_different_branch",
        "cold_plus_warm_access",
        "empty",
    ],
)
def test_sload(blockchain_test: BlockchainTestFiller, fork: str, storage_slot_accesses):
    """
    Test SLOAD witness.
    """
    witness = Witness()
    for slot in storage_slot_accesses:
        witness.add_storage_slot(TestAddress2, slot, TestAddress2Storage.get(slot))

    _sload(blockchain_test, fork, storage_slot_accesses, witness)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
def test_sload_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str):
    """
    Test SLOAD with insufficient gas.
    """
    witness = Witness()
    for slot in [1000, 1001]:
        witness.add_storage_slot(TestAddress2, slot, TestAddress2Storage.get(slot))

    _sload(blockchain_test, fork, [1000, 1001, 1002, 1003], witness, gas_limit=1_024)


def _sload(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    storage_slot_accesses: list[int],
    extra_witness: Witness,
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
            code=code,
            storage=TestAddress2Storage,
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

    witness = Witness()
    witness.add_account_full(env.fee_recipient, None)
    witness.add_account_full(TestAddress, pre[TestAddress])
    witness.add_account_full(TestAddress2, pre[TestAddress2])
    witness.merge(extra_witness)

    blockchain_test(
        genesis_environment=env,
        pre=pre,
        post={},
        blocks=blocks,
        witness=witness,
    )
