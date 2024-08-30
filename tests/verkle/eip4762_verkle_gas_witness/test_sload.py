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
def test_sload(blockchain_test: BlockchainTestFiller, storage_slot_accesses):
    """
    Test SLOAD witness.
    """
    witness_check_extra = WitnessCheck()
    for slot in storage_slot_accesses:
        witness_check_extra.add_storage_slot(TestAddress2, slot, TestAddress2Storage.get(slot))

    _sload(blockchain_test, storage_slot_accesses, witness_check_extra)


# TODO(verkle): update to Osaka when t8n supports the fork.
@pytest.mark.valid_from("Verkle")
def test_sload_insufficient_gas(blockchain_test: BlockchainTestFiller, fork: str):
    """
    Test SLOAD with insufficient gas.
    """
    witness_check_extra = WitnessCheck()
    for slot in [1000, 1001]:
        witness_check_extra.add_storage_slot(TestAddress2, slot, TestAddress2Storage.get(slot))

    _sload(blockchain_test, [1000, 1001, 1002, 1003], witness_check_extra, gas_limit=21_024)


def _sload(
    blockchain_test: BlockchainTestFiller,
    fork: str,
    storage_slot_accesses: list[int],
    witness_check_extra: WitnessCheck,
    gas_limit=1_000_000,
):
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
        number=1,
        timestamp=1000,
    )
    code = Bytecode()
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

    witness_check = witness_check_extra
    for address in [TestAddress, TestAddress2, env.fee_recipient]:
        witness_check.add_account_full(
            address=address,
            account=(None if address == env.fee_recipient else pre[address]),
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
        post={},
        blocks=blocks,
    )
